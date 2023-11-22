# Reverse Engineering 23 - GraalPy Log Analysis

## Setup
1. Make sure you have docker and docker-compose available. :)
2. Clone the repository.
3. Download the python packages to test to the local file system by executing the [`mirror_repos.py`](./repos/mirror_repos.py) script inside the [repos](./repos) directory.<br>
Note that you will need to have python3 as well as the `requests` package installed for that.
4. Check the `sources_mirror` directory inside the [repos](./repos) directory that is created during the process.<br>
It should contain various tarball archives respective to the specified packages in [`pypi_list_repo.json`](./repos/pypi_list_repo.json).

## Test Execution
Simply run `docker-compose up tests` in the repository.
Use the `--force-recreate` option in order to apply changes in the file system by recreating the container.

It should create the docker image as well as execute the tests based on the locally downloaded repositories.
Therefore, it uses the [`library_tester.py`](./tests/library_tester.py) script.

During the testing process, result files are dumped in the [results](./results) directory.

## Result Browsing
In order to browse through the result files we implemented a lightweight React application.
You can find the code inside the [results-browser](./results-browser) directory.

### Setup
To make the application aware of the result files, you will need to execute the [`results_index.sh`](./results/results_index.sh) script inside the [results](./results) directory.
It will output a `results_index.json` file which you need to copy into the [results-browser/public](./results-browser/public) directory.

### Startup
Execute `npm start` inside the [results-browser](./results-browser) directory to start the application.
On [localhost:3000](http://localhost:3000) you can now browse through the files.
