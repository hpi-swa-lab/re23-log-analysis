# Log Analysis

This folder contains scripts and webapps to analyse the test logs.

You can use use `analyse-graalpy-failures.py` to analyse the failures of the GraalPython tests. You can use different flags to filter, group, print and plot errors. Use `analyse-graalpy-failures.py --help` to see all options.

The script `compare-cpython-graalpy.py` compares the output of the tests with a CPython and GraalPython interpreter in a CSV.

Run `python app.py` to start a webapp that shows an interactive view of the test results. You can filter them with and group them by different criteria (in the future). The webapp is based on [Dash](https://dash.plot.ly/).
