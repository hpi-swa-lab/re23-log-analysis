#!/bin/bash

# Note that the script should run in a docker container with sufficient path mappings!
# /opt/repos, /opt/tests and /tmp/results need to get mapped.

# For each already downloaded tarball file in /opt/repos/sources_mirror
for tarball in /opt/repos/sources_mirror/*.tar.xz; do
  tarball_basename=$(basename "${tarball}")
  # extracting follows https://unix.stackexchange.com/a/137785
  tarball_without_ending=${tarball_basename%.tar.xz}
  echo "--- Testing ${tarball_without_ending} ---"

  # At this point tarball_without_ending should look like "<package>-<version>"
  name=${tarball_without_ending%-*} # remove everything after the last "-"
  version=${tarball_without_ending##*-} # remove all before the last "-"

  # Prepare test result directory (clear and recreate)
  rm -rf "/tmp/results/${name}"
  mkdir "/tmp/results/${name}"
  # Specify a dedicated result file for a summary of the test execution
  result_file=/tmp/results/${name}/test_summary.json


  # Step 1: copy the tarball into WORK_DIR (env variable is set in the Dockerfile)
  cp "${tarball}" "${WORK_DIR}"

  # Step 2: execute the library_tester.py script with the name and version of the package,
  # configure it to be test run 1 and reference the result file for the summary.
  "${CPYTHON_PATH}" /opt/tests/library_tester.py -n "${name}" -v "${version}" -t 1 -l "${result_file}"

  # Step 3: dump additional (log) files created while testing
  cp ${WORK_DIR}/results/${name}/${version}/1/*.log /tmp/results/${name}
done
