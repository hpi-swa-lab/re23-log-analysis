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
