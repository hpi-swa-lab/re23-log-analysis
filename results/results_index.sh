#!/bin/bash

# Store the content of the results directory as json, so we can browse through them in a webapp.
# This script and the resulting json file get ignored.
# Note that you need to have `tree` installed (unix/wsl).

tree . -U -f --noreport -I "results_index.*" -J -o results_index.json
