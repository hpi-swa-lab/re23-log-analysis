#!/bin/bash

# The following script is supposed to be run in this results directory only.

# Pack and compress down the graalpy-tmp directories that were output for debugging purposes.
GRAALPY_TMP_DIR="graalpy-tmp"
for fileOrDir in *; do
    if [ -d "$fileOrDir" ]; then
      cd "./$fileOrDir" || continue
      if [ -d "$GRAALPY_TMP_DIR" ]; then
        echo "Packing $fileOrDir/$GRAALPY_TMP_DIR files into $fileOrDir/$GRAALPY_TMP_DIR.tar.gz"
        tar --remove-files -czf graalpy-tmp.tar.gz graalpy-tmp
      fi
		  cd ..
    fi
done

# Then store the content of the results directory as json, so we can browse through them in a webapp.
# This script and the resulting json file get ignored.
# Note that you need to have `tree` installed (unix/wsl).
echo "--- Creating the index of result files ---"
tree . -D --timefmt "%Y-%m-%dT%H:%M:%S%z" -s -U -f --noreport -I "results_index.*" -J -o results_index.json
