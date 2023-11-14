#!/usr/bin/env python3
import sys

import abc
import argparse
import json
import os
import re
import requests
import shutil
import subprocess

BUCKET = 'mt_data'
SOURCES_MIRROR = 'sources_mirror'
DIR = os.path.dirname(__file__)


def trim_version(version, places):
    return '.'.join(version.split('.')[:places])


class DownloadHandler(abc.ABC):
    handlers = {}

    @abc.abstractmethod
    def download(self, name, version, data, destdir):
        pass

    def __init_subclass__(cls, handler_name=None):
        if handler_name:
            if handler_name in cls.handlers:
                raise RuntimeError(f"Duplicate download handler {handler_name}")
            cls.handlers[handler_name] = cls()

    @classmethod
    def find_handler(cls, handler_name: str):
        return cls.handlers.get(handler_name)


class DefaultDownloadHandler(DownloadHandler, handler_name='default'):
    @staticmethod
    def get_possible_versions(package, version, data):
        rule = data.get('tag_from_version')
        if rule:
            return [re.sub(rule['regex'], rule['replacement'], version, count=1)]
        if package == "opencv-contrib-python" or package == "opencv-python" or package == "opencv-python-headless":
            return [version[version.rindex(".") + 1:len(version)]]
        if package == "protobuf":
            return ["v{}".format(version[version.index(".") + 1:len(version)])]

        possible_versions = [
            prefix + v
            for v in (version, version.replace('.', '_'), version.replace('.', '-'), version + '.0')
            for prefix in
            ('', 'v', 'v.', package + '-', package + '_', package.lower() + '-', package.lower() + '_', 'release-',
             'release_', 'rel_', 'release_v', 'RELEASE_', 'pypi-v', 'version-')
        ]
        date_match = re.match(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', version)
        if date_match:
            possible_versions += [
                '{}.{:02}.{:02}'.format(*map(int, date_match.groups())),
                '{}.{:02}.{}'.format(*map(int, date_match.groups())),
            ]
        return possible_versions

    def download(self, name, version, data, destdir):
        nv = f'{name}-{version}'
        url = data.get('repo_url')
        if not url:
            raise RuntimeError("Missing source URL")

        possible_versions = self.get_possible_versions(name, version, data)
        for version_string in possible_versions:
            cmd = ["git", "clone", "-b", version_string, url, nv]
            if not data.get('deep_clone'):
                cmd += ["--depth", "1"]
            if not data.get('no_submodules'):
                cmd += ["--recurse-submodules"]
            retvalue = subprocess.call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=destdir,
            )
            if retvalue == 0:
                return os.path.join(destdir, nv)
        else:
            raise RuntimeError(f"Failed to find a tag for version. Tried: {possible_versions}")


class MercurialDownloadHandler(DownloadHandler, handler_name='mercurial'):
    def download(self, name, version, data, destdir):
        nv = f'{name}-{version}'
        outdir = os.path.join(destdir, nv)
        url = data.get('repo_url')
        if not url:
            raise RuntimeError("Missing source URL")
        subprocess.run(["hg", "clone", url, nv], cwd=destdir, check=True)
        subprocess.run(["hg", "checkout", version], cwd=outdir, check=True)
        return outdir


class DownloadArchiveHandler(DownloadHandler, handler_name='download_archive'):
    def get_url(self, name, version, data):
        url = data.get('download_url')
        if not url:
            raise RuntimeError("Missing download_url")
        url = url.format(name=name, version=version)
        assert '{' not in url
        return url

    def download(self, name, version, data, destdir):
        url = self.get_url(name, version, data)
        output_path = os.path.join(destdir, f"{name}-{version}")
        shutil.rmtree(output_path, ignore_errors=True)
        os.makedirs(output_path)
        subprocess.run(
            ["curl", url, "-fLO"],
            cwd=output_path,
            check=True,
        )
        archive = os.listdir(output_path)[0]
        if archive.endswith('.zip'):
            cmd = ['unzip', archive]
        else:
            cmd = ['tar', 'xf', archive]
        subprocess.run(cmd, cwd=output_path, check=True)
        os.unlink(os.path.join(output_path, archive))
        if len(os.listdir(output_path)) == 1:
            # Move a level up
            tmp_path = f"{output_path}.tmp"
            os.rename(output_path, tmp_path)
            os.rename(os.path.join(tmp_path, os.listdir(tmp_path)[0]), output_path)
            os.rmdir(tmp_path)
        return output_path


class BeautifulSoup4Handler(DownloadArchiveHandler, handler_name='beautifulsoup4'):
    def get_url(self, name, version, data):
        base_url = "https://www.crummy.com/software/BeautifulSoup/bs4/download"
        return f"{base_url}/{trim_version(version, 2)}/{name}-{version}.tar.gz"


class DownloadPyPISourceArchiveHandler(DownloadArchiveHandler, handler_name='pypi_source'):
    def get_url(self, name, version, data):
        response = requests.get(f"https://pypi.org/pypi/{name}/json")
        if response.status_code != 200:
            raise RuntimeError("Unable to get PyPI metadata")
        release = response.json()['releases'].get(version)
        if not release:
            raise RuntimeError("Unable to get PyPI release")
        for file in release:
            if file['packagetype'] == 'sdist':
                return file['url']
        raise RuntimeError("Unable to get PyPI source archive")


class TypeshedDownloadHandler(DownloadHandler, handler_name="typeshed"):
    def download(self, name, version, data, destdir):
        nv = f'{name}-{version}'
        url = data.get('repo_url')
        if not url:
            raise RuntimeError("Missing source URL")
        pypi_source = DownloadPyPISourceArchiveHandler().download(name, version, data, destdir)
        with open(f"{pypi_source}/PKG-INFO") as f:
            pkg_info = f.read()
        shutil.rmtree(pypi_source, ignore_errors=True)

        match = re.search(r"This package was generated from typeshed commit `([0-9a-f]+)`", pkg_info)
        if match:
            commit = match.group(1)
        else:
            raise RuntimeError("Couldn't determine typeshed commit")

        subprocess.run(
            ["git", "clone", "--recurse-submodules", url, nv],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=destdir,
            check=True,
        )
        output_path = os.path.join(destdir, nv)
        subprocess.run(
            ["git", "checkout", commit],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=output_path,
            check=True,
        )
        return output_path
    
    class CommitDownloadHandler(DownloadHandler, handler_name="commit"):
        def download(self, name, version, data, destdir):
            nv = f'{name}-{version}'
            url = data.get('repo_url')
            commit = data.get('commit')

            subprocess.run(
                ["git", "clone", "--recurse-submodules", url, nv],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=destdir,
                check=True,
            )
            output_path = os.path.join(destdir, nv)
            subprocess.run(
                ["git", "checkout", commit],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=output_path,
                check=True,
            )
            return output_path


def mirror_repos(repos, upload=False, force=False, all_packages=False):
    os.makedirs(SOURCES_MIRROR, exist_ok=True)
    existing_files = set()
    skipped = 0
    success = True
    if all_packages and upload and not force:
        cmd = ['oci', 'os', 'object', 'list', '--bucket-name', BUCKET, '--prefix', 'python-sources/', '--all']
        result = json.loads(subprocess.check_output(cmd, universal_newlines=True))
        existing_files = {f['name'] for f in result['data']}
    for name, data in repos.items():
        handler_name = data.get('download_handler', 'default')
        handler = DownloadHandler.find_handler(handler_name)
        if not handler:
            print(f"WARNING: no handler {handler_name!r} found for package {name!r}")
            continue
        version = data['version']
        nv = f'{name}-{version}'
        path = os.path.join(SOURCES_MIRROR, nv)
        shutil.rmtree(path, ignore_errors=True)
        tarball = '{}.tar.xz'.format(nv)
        upload_name = 'python-sources/{}'.format(tarball)
        if upload_name in existing_files:
            skipped += 1
            continue
        try:
            handler.download(name, version, data, SOURCES_MIRROR)
        except Exception as e:
            print(f"WARNING: Failed to download {nv}: {e}")
            success = False
            continue
        subprocess.check_output(['tar', '-cJf', tarball, nv], cwd=SOURCES_MIRROR)
        if upload:
            print(f"Uploading {nv}")
            subprocess.check_output(
                ['oci', 'os', 'object', 'put', '--force', '--bucket-name', BUCKET,
                 '--file', tarball, '--name', upload_name],
                cwd=SOURCES_MIRROR,
            )
    if skipped:
        print(f"Skipped {skipped} already existing tarballs")
    return success


def main():
    parser = argparse.ArgumentParser(
        description="""
            This script is supposed to be used on the gateway machine to upload the package sources
            to the object storage. It can also be used locally to obtain sources for local run with --no-upload
            """,
    )
    parser.add_argument('--no-upload', action='store_false', dest='upload', help="Skip OCI upload")
    parser.add_argument('--force', action='store_true', help="Force upload even if already existing")
    parser.add_argument('packages', nargs='*', help="Restrict the download set to only these packages")
    args = parser.parse_args()

    with open(os.path.join(DIR, 'pypi_list_repo.json')) as f:
        repos = json.loads(f.read())

    if args.packages:
        repos = {p: d for p, d in repos.items() if p in args.packages}

    success = mirror_repos(repos, all_packages=not args.packages, upload=args.upload, force=bool(args.force or args.packages))
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
