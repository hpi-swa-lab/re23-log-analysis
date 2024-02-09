# Reverse Engineering 23 - GraalPy Log Analysis

## File Structure

- [tests](./tests) - Contains the test execution environment.
- [repos](./repos) - Contains the python packages to test.
- [results](./results) - Contains the result files of the test execution.
- [results-browser](./results-browser) - Contains the result browsing application for the testing-pipeline.
- [analyse](./analyse) - Contains scripts and webapps to analyse the output of individual test frameworks.

## Analysis of the Execution Environment

### Setup

1. Make sure you have docker and docker-compose available. :)
2. Clone the repository.
3. Download the python packages to test to the local file system by executing the [`mirror_repos.py`](./repos/mirror_repos.py) script inside the [repos](./repos) directory.<br>
Note that you will need to have python3 as well as the `requests` package installed for that.
4. Check the `sources_mirror` directory inside the [repos](./repos) directory that is created during the process.<br/>
It should contain various tarball archives respective to the specified packages in [`pypi_list_repo.json`](./repos/pypi_list_repo.json).

### Test Execution

Simply run `docker-compose up tests` in the repository.
Use the `--force-recreate` option in order to apply changes in the file system by recreating the container.

It should create the docker image as well as execute the tests based on the locally downloaded repositories.
Therefore, it uses the [`library_tester.py`](./tests/library_tester.py) script.

During the testing process, result files are dumped in the [results-browser/public/results](./results-browser/public/results) directory.

### Result Browsing Application

In order to browse through the result files we implemented a lightweight React application.
You can find the code inside the [results-browser](./results-browser) directory.

#### Setup

To make the application aware of the result files, you will need to execute the [`results_index.sh`](./results-browser/public/results/results_index.sh) script inside the [results-browser/public/results](./results-browser/public/results) directory.
The script will create a `results_index.json` file which indexes all result files that were dumped in the directory during the testing process.

Also, you will need to execute the `npm install` command in the [results-browser](/results-browser) directory in order to install all dependencies for the application.

#### Startup

Execute the `npm start` command inside the [results-browser](./results-browser) directory to start the application.
On [localhost:3000](http://localhost:3000) you can now browse through the files.

The application reads in all file contents into memory in order to filter/display it.
So depending on the size of the [results-browser/public/results](./results-browser/public/results) directory, this might take some time.

## Analyse the Testing Framework

This folder [analyse](analyse/) contains scripts and webapps to analyze the output of individual testing frameworks.

You can use use `analyse-graalpy-failures.py` to analyse the failures of the GraalPython tests. You can use different flags to filter, group, print and plot errors. Use `analyse-graalpy-failures.py --help` to see all options.

The script `compare-cpython-graalpy.py` compares the output of the tests with a CPython and GraalPython interpreter in a CSV.

Run `python app.py` to start a webapp that shows an interactive view of the test results. You can filter them with and group them by different criteria (in the future). The webapp is based on [Dash](https://dash.plot.ly/).
