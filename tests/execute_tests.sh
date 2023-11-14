#!/bin/bash

# Note that the script should run in a docker container with sufficient path mappings!
# /opt/repos, /opt/tests and /tmp/results need to get mapped.

# For each already downloaded tarball file in /opt/repos/sources_mirror
for tarball in /opt/repos/sources_mirror/*.tar.xz; do
  tarball_basename=$(basename "${tarball}")
  # extracting follows https://unix.stackexchange.com/a/137785
  tarball_without_ending=${tarball_basename%.tar.xz}
  echo "Testing ${tarball_without_ending}..."

  # At this point tarball_without_ending should look like "<package>-<version>"
  name=${tarball_without_ending%-*} # remove everything after the last "-"
  version=${tarball_without_ending##*-} # remove all before the last "-"

  # Prepare test result file (create directory if not existing, and rm previous file)
  mkdir -p "/tmp/results/$(date -I)/${name}"
  result_file=/tmp/results/${name}/results.json
  rm -f result_file

  # Step 1: copy the tarball into WORK_DIR (env variable is set in the Dockerfile)
  cp "${tarball}" "${WORK_DIR}"

  # Step 2: execute /opt/tests/library_tester.py with the name and version of the package
  # configure it to be test run 1 and specify a respective result file.
  "${CPYTHON_PATH}" /opt/tests/library_tester.py -n "${name}" -v "${version}" -t 1 -l "${result_file}"
  # TODO: script fails at imports from common.result at the moment

  # TODO: Step 3: If the json file is not sufficient, collect stdout log output and dump it as well
  # TODO: How does junit-xml work with this?
done
