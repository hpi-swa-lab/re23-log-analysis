#!/usr/bin/env python3
from __future__ import annotations

from os import PathLike

import argparse
import configparser
import contextlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import toml
import traceback
from contextlib import suppress
from dataclasses import dataclass
from datetime import timedelta, datetime
from itertools import chain
from pathlib import Path
from textwrap import dedent

from common.result import TestResult, TestResultCounts
from python.result_parsers import parse_log, parse_junit_xml

DIR = Path(__file__).parent
IS_PRODUCTION = os.environ.get("TESTER_ENV") == 'production'
BUCKET = 'mt_data'

GRAALPY_ENV_VARS = {
    'VIRTUALENV_CREATOR': 'venv',
    'VIRTUALENV_SEEDER': 'graalpy',
}

DEFAULT_TIMEOUTS = {
    'cpython_install': {'minutes': 20},
    'cpython_test': {'hours': 2},
    'graalpy_install': {'hours': 3},
    'graalpy_test': {'hours': 3},
}


@contextlib.contextmanager
def timed_result(result: TestResult):
    start_time = datetime.now()
    try:
        yield
    finally:
        result.test_duration = datetime.now() - start_time


@contextlib.contextmanager
def print_hrule(title):
    begin = f' BEGIN {title.upper()} '
    print(f'{begin:=^80}')
    try:
        yield
    finally:
        end = f' END {title.upper()} '
        print(f'{end:=^80}\n')


def run_command(cmd: list[str], result: TestResult, message: str, *, timeout: timedelta | None = None,
                virtualenv_path: Path | None = None, **kwargs):
    log_path = Path(result.log_path).absolute()
    tee_cmd = ['tee', '-ia', str(log_path)]
    script = [
        'set -eo pipefail',
        'ulimit -c 0',
    ]
    if virtualenv_path:
        script.append(f'source {shlex.quote(str(virtualenv_path.absolute() / "bin" / "activate"))}')
    script.append(f'exec {shlex.join(cmd)} &> >({shlex.join(tee_cmd)})')
    cmd = ['bash', '-c', '\n'.join(script)]
    start_time = datetime.now()
    with (
        print_hrule(message),
        subprocess.Popen(cmd, **kwargs, start_new_session=True) as process,
    ):
        pgid = os.getpgid(process.pid)
        try:
            return process.wait(timeout=(timeout.total_seconds() if timeout else None))
        except subprocess.TimeoutExpired:
            with open(log_path, 'a') as log:
                for f in sys.stdout, log:
                    print(f"\n{'*' * 80}\nTimeout exceeded, sending SIGINT to process\n{'*' * 80}", file=f)
                # Try to first interrupt the process group, hoping that it will print a traceback of where it got stuck
                with suppress(OSError):
                    os.killpg(pgid, signal.SIGINT)
                with suppress(subprocess.TimeoutExpired):
                    process.wait(timeout=5)
                with suppress(OSError):
                    os.killpg(pgid, signal.SIGKILL)
                for f in sys.stdout, log:
                    print(f"*** Timed out after {timeout}", file=f)
                raise
        finally:
            result.test_duration = datetime.now() - start_time


class TestError(Exception):
    pass


@dataclass(frozen=True)
class Interpreter:
    name: str
    path: PathLike
    env: dict[str, str]
    reference_impl: bool

    def __str__(self):
        return self.name


def get_timeout(metadata: dict, timeout_name: str) -> timedelta:
    if timeouts := metadata.get('timeouts'):
        if timeout := timeouts.get(timeout_name):
            return timedelta(**timeout)
    return timedelta(**DEFAULT_TIMEOUTS[timeout_name])


def upload_wheel(name: str, path: Path):
    try:
        version_out = subprocess.run(
            [str(DIR / 'version-lister-python.sh')],
            text=True,
            capture_output=True,
            check=True,
        )
        version_info = json.loads(version_out.stdout)
        if not version_info['vm_version_short'].endswith('-dev'):
            print("Not uploading wheels for a released version")
            return
        upload_name = f'python/repository/{name}/{path.name}'
        if IS_PRODUCTION:
            subprocess.run(
                [
                    'oci', '--auth', 'instance_principal', 'os', 'object', 'put', '--force',
                    '--bucket-name', BUCKET,
                    '--file', str(path),
                    '--name', upload_name,
                ],
                check=True,
            )
        else:
            print(f"Would upload {path} as {upload_name}")
    except Exception:
        print("Failed to upload wheel:", file=sys.stderr)
        traceback.print_exc()


class Tester:
    def __init__(self, *, work_dir: Path, results_dir: Path, name: str, version: str, metadata: dict):
        self.work_dir = work_dir
        self.results_dir = results_dir
        self.name = name
        self.version = version
        self.metadata = metadata
        self.source_dir = None
        self.test_dir = None

    def unpack_sources(self):
        nv = f"{self.name}-{self.version}"
        self.source_dir = self.work_dir / nv
        shutil.rmtree(self.source_dir, ignore_errors=True)
        tarball_name = f"{nv}.tar.xz"
        if IS_PRODUCTION:
            print(f"Downloading {tarball_name}")
            return_value = subprocess.call(
                [
                    'oci', '--auth', 'instance_principal', 'os', 'object', 'get', '--bucket-name', BUCKET,
                    '--name', f'python-sources/{tarball_name}', '--file', tarball_name,
                ],
                cwd=self.work_dir,
            )
            if return_value:
                raise TestError("Failed to download tarball")
            self.extract_tarball(tarball_name)
        elif Path(tarball_name).is_file():
            self.extract_tarball(tarball_name)
        else:
            print(f"Downloading {nv}")
            download_path = self.work_dir / 'sources_mirror' / nv
            return_value = subprocess.call([str(DIR / 'mirror_repos.py'), '--no-upload', self.name], cwd=self.work_dir)
            if return_value or not download_path.exists():
                raise TestError("Failed to download tarball")
            os.rename(download_path, self.work_dir / nv)
        if not self.source_dir.exists():
            existing_files = map(str, self.source_dir.iterdir())
            raise TestError(
                f"Source didn't extract to expected directory {nv}. Existing files: {', '.join(existing_files)}"
            )
        self.test_dir = self.source_dir
        if subdirectory := self.metadata.get('subdirectory'):
            self.test_dir = self.test_dir / subdirectory

    def extract_tarball(self, tarball_name):
        print(f"Extracting {tarball_name}")
        return_value = subprocess.call(['tar', 'xf', tarball_name], cwd=self.work_dir)
        if return_value:
            raise TestError("Failed to extract tarball")

    def apply_patch(self, results):
        patch_path = DIR / 'patches' / f'{self.name}.patch'
        if patch_path.exists():
            patch_log_path = self.results_dir / 'patch.log'
            patch_result = TestResult(name='patch', log_path=patch_log_path, auxiliary=True)
            results.append(patch_result)
            with open(patch_path) as patch:
                returncode = run_command(
                    ['patch', '-p1'],
                    patch_result,
                    message='applying patch',
                    stdin=patch,
                    cwd=self.source_dir,
                )
                if returncode:
                    raise TestError(f"*** Failed to apply patch file {patch_path.name}")

    def get_timeout(self, timeout_name: str) -> timedelta:
        return get_timeout(self.metadata, timeout_name)

    def generate_tox_file(self):
        with open(self.test_dir / 'tox.ini', 'w') as tox_ini_file:
            isolated_build = False
            pyproject_toml_file = self.test_dir / 'pyproject.toml'
            if pyproject_toml_file.exists():
                with open(pyproject_toml_file) as pyproject_toml_file:
                    pyproject_toml = toml.load(pyproject_toml_file)
                    if legacy_tox_ini := pyproject_toml.get('tool', {}).get('tox', {}).get('legacy_tox_ini'):
                        tox_ini_file.write(f"# MCD: Automatically copied from pyproject.toml's legacy_tox_ini key\n")
                        tox_ini_file.write(legacy_tox_ini)
                        return
                    if pyproject_toml.get('build-system', {}).get('build-backend'):
                        isolated_build = True
            use_unittest = False
            setup_py = self.test_dir / 'setup.py'
            if setup_py.exists():
                with open(setup_py) as setup_file:
                    if match := re.search(r'test_suite\s*=\s*(.*)', setup_file.read()):
                        use_unittest = 'nose' not in match.group(1)
            deps = []
            if use_unittest:
                commands = '{envpython} setup.py test'
                deps += ['mock']
            else:
                commands = 'pytest --tb=native -v'
                deps += ['pytest', 'mock']
            unwanted_requirements = ('docs', 'flake', 'pylint', 'black', '2', '3')
            for requirements_file in chain(self.test_dir.rglob('*requirements*.txt'),
                                           self.test_dir.glob('*requirements*/*.txt')):
                rel_path = str(requirements_file.relative_to(self.test_dir))
                if not any(unwanted in rel_path for unwanted in unwanted_requirements):
                    deps.append(f'-r{rel_path}')
            tox_ini = configparser.ConfigParser()
            if isolated_build:
                tox_ini['tox'] = {'isolated_build': True}
            tox_ini['testenv'] = {
                'commands': commands,
                'deps': '\n'.join(deps),
            }
            tox_ini.write(tox_ini_file)

    def test_installs(self, interpreter: Interpreter) -> TestResult:
        timeout = self.get_timeout(f'{interpreter.name}_install')
        log_path = self.results_dir / f'{interpreter}-install.log'
        result = TestResult(name=f'{interpreter}-install', log_path=log_path, reference_impl=interpreter.reference_impl)
        venv_path = (self.work_dir / 'install-virtualenv').absolute()
        shutil.rmtree(venv_path, ignore_errors=True)
        print(f"Creating a virtualenv with {interpreter}")
        process_result = subprocess.run(
            ['virtualenv', '--no-download', '--python', str(interpreter.path),
             str(venv_path)],
            cwd=self.work_dir,
            env=interpreter.env,
            stdout=subprocess.DEVNULL,
        )
        if process_result.returncode != 0:
            print(f"*** Virtualenv creation with {interpreter} failed with return code {process_result.returncode}")
            return result
        cmd = ['pip', 'install', f'{self.name}=={self.version}']
        print(f"Running command: {shlex.join(cmd)}")
        try:
            returncode = run_command(
                cmd,
                result,
                virtualenv_path=venv_path,
                message=f"installation ({interpreter})",
                cwd=self.work_dir,
                env=interpreter.env,
                timeout=timeout,
            )
            result.installs = returncode == 0
        except subprocess.TimeoutExpired:
            with open(result.log_path, 'a') as log:
                for f in sys.stdout, log:
                    print(f"*** Installation timed out on {interpreter} after {timeout}", file=f)
            result.installs = False
        if interpreter.name == 'graalpy':
            # Ignore errors, this upload is optional
            cmd = [f'{venv_path}/bin/pip', 'cache', 'list', '--format=abspath', f'{self.name}-{self.version}-graalpy']
            pip_output = subprocess.run(cmd, capture_output=True, text=True, )
            if pip_output.returncode == 0:
                for line in pip_output.stdout.split('\n'):
                    if line:
                        upload_wheel(self.name, Path(line))
        return result

    def run_tests(self, interpreter: Interpreter) -> TestResult:
        timeout = self.get_timeout(f'{interpreter.name}_test')
        log_path = self.results_dir / f'{interpreter}-test.log'
        tox_factors = self.metadata.get('tox_factors', ['unit', 'test', 'tests'])
        if any(re.match(r'py\d+', factor) for factor in tox_factors):
            raise RuntimeError("It is not allowed to specify one of the base interpreter factors in tox_factors")
        testenv = f'{interpreter}libtest-{"-".join(tox_factors)}'
        with open(self.test_dir / 'tox.ini', 'a') as f:
            f.write('\n' + dedent(f'''\
            [testenv:{testenv}]
            basepython = {interpreter.path}
            passenv =
                HOME
                VIRTUALENV_*
                PIP_*
                CMAKE_*
                *THREAD*
                PYO_TEST_*
                ORACLE_HOME
            ''') + '\n')
        cmd = ['tox', '-c', 'tox.ini', '-e', testenv]
        print(f"Running command: {shlex.join(cmd)}")
        result = TestResult(name=f'{interpreter}-test', log_path=log_path, reference_impl=interpreter.reference_impl)
        try:
            returncode = run_command(
                cmd,
                result,
                message=f'test output ({interpreter})',
                cwd=self.test_dir,
                env=interpreter.env,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            # Don't report partial results for CPython because we need accurate test totals. For GraalPy it's fine
            # because we know how many tests there were supposed to be from the CPython run, and we mark the missing
            # ones as failures
            if interpreter.name == 'cpython':
                return result
        else:
            print(f"Tests command finished with return code {returncode} after {result.test_duration}")
        try:
            if junit_xml := self.metadata.get('junit_xml'):
                files = list(self.test_dir.rglob(junit_xml))
                result.counts = parse_junit_xml(files)
                for file in files:
                    os.unlink(file)
            else:
                result.counts = parse_log(log_path, strict=(interpreter.name == 'cpython'))
            if result.counts:
                print(f"Test results for {interpreter} - {result.counts}")
            else:
                print(f"Couldn't parse test results or no tests executed for {interpreter}")
        except Exception:
            print("Result parsing crashed")
            traceback.print_exc()
        return result


def prepare_env(name: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    # Don't use the mirror for packages that test pip internals, it causes spurious failures
    if name in ('setuptools', 'pip'):
        env.pop('PIP_INDEX_URL', None)
        env.pop('PIP_TRUSTED_HOST', None)
    return env


def get_metadata(name: str):
    metadata_path = DIR / 'pypi_list_repo.json'
    with open(metadata_path) as f:
        metadata = json.load(f)
    if name not in metadata:
        sys.exit(f"Package {name!r} not found in metadata")
    return metadata[name]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', required=True, help="Package name")
    parser.add_argument('-v', '--version', help="Package version")
    parser.add_argument('-t', '--run-number', default='1', help="Test run number")
    parser.add_argument('-l', '--results-file', default='result', help="Test results filename")
    parser.add_argument('-u', help="ignored, backwards compatibility")
    only_group = parser.add_mutually_exclusive_group()
    only_group.add_argument('--test-only', action='store_false', dest="test_installation")
    only_group.add_argument('--install-only', action='store_false', dest="run_tests")
    only_group = parser.add_mutually_exclusive_group()
    only_group.add_argument('--cpython-only', action='store_false', dest="test_graalpy")
    only_group.add_argument('--graalpy-only', action='store_false', dest="test_cpython")

    args = parser.parse_args()

    name = args.name

    metadata = get_metadata(name)
    version = metadata['version']
    if args.version and args.version != version:
        sys.exit(f"Given version doesn't match metadata version - {args.version!r} != {version!r}")

    work_dir = Path(os.environ.get('WORK_DIR', 'workdir'))
    results_dir = work_dir / 'results' / 'python' / name / version / args.run_number
    os.makedirs(results_dir, exist_ok=True)

    tester = Tester(
        work_dir=work_dir,
        results_dir=results_dir,
        name=name,
        version=version,
        metadata=metadata,
    )
    results = []
    cpython = Interpreter(
        name='cpython',
        reference_impl=True,
        path=os.environ.get('CPYTHON_PATH', 'python'),
        env=prepare_env(name),
    )
    graalpy = Interpreter(
        name='graalpy',
        reference_impl=False,
        path=os.environ.get('GRAALPY_PATH', 'graalpy'),
        env=prepare_env(name) | GRAALPY_ENV_VARS,
    )

    try:
        if args.test_installation:
            if args.test_cpython:
                results.append(tester.test_installs(cpython))
            if args.test_graalpy:
                results.append(tester.test_installs(graalpy))

        if args.run_tests:
            tester.unpack_sources()
            tester.apply_patch(results)

            tox_ini = tester.test_dir / 'tox.ini'
            tox_ini_msg = 'tox.ini'
            if not tox_ini.exists():
                tox_ini_msg = 'tox.ini (generated)'
                tester.generate_tox_file()
                # n.b. cannot be named tox.ini, that screws up mime type on the mirror
                upload_path = results_dir / 'tox-ini.log'
                shutil.copy(tox_ini, upload_path)
                results.append(TestResult(name='tox.ini', log_path=upload_path, auxiliary=True))

            cpython_test_result = None
            if args.test_cpython:
                with open(tox_ini) as f, print_hrule(tox_ini_msg):
                    print(f.read())
                cpython_test_result = tester.run_tests(cpython)
                results.append(cpython_test_result)
                if not cpython_test_result.counts or cpython_test_result.counts.passed == 0:
                    raise TestError("CPython didn't finish tests, not running GraalPy")

            if args.test_graalpy:
                with open(tox_ini) as f, print_hrule(tox_ini_msg):
                    print(f.read())
                graalpy_test_result = tester.run_tests(graalpy)
                results.append(graalpy_test_result)
                if cpython_test_result:
                    # If GraalPy failed to finish, report it as if it failed everything that CPython passed
                    if not graalpy_test_result.counts:
                        graalpy_test_result.counts = TestResultCounts()
                    # Many packages run multiple test sessions. It's possible we're missing counts from some of them
                    # entirely. If the CPython run contains more tests, mark the missing ones as failure.
                    unexecuted_tests = cpython_test_result.counts.total - graalpy_test_result.counts.total
                    allow_lower_total = (
                            metadata.get('allow_lower_total_on_graalpy') and graalpy_test_result.counts.total
                    )
                    if unexecuted_tests > 0 and not allow_lower_total:
                        graalpy_test_result.counts = TestResultCounts(
                            passed=graalpy_test_result.counts.passed,
                            skipped=graalpy_test_result.counts.skipped,
                            failed=graalpy_test_result.counts.failed + unexecuted_tests,
                            unknown=graalpy_test_result.counts.unknown,
                        )
    except TestError as e:
        print(e)
        # Just submit the current results
    results = [result.as_dict() for result in results]
    with open(args.results_file, 'w') as f1:
        json.dump(results, f1)
    with print_hrule("final output"):
        json.dump(results, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
