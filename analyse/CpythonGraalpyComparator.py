from TestResult import TestResult
from JunitXMLParser import JunitXMLParser
import os
import csv


def _load_and_extract_files(files, result_dict):
    for package, file in files:
        if os.path.isfile(file):
            xml_parser = JunitXMLParser(file)
            result_dict[package] = TestResult(
                True,
                xml_parser.get_errors(),
                xml_parser.get_failures(),
                xml_parser.get_skipped(),
                xml_parser.get_tests(),
            )
        else:
            result_dict[package] = TestResult(False)


class CpythonGraalpyComparator(object):
    """
    A class to create a summary about the test results of CPython and GraalPython.
    Use to compare the number of passed, skipped, failed and erroneous tests in both
    """

    def __init__(self, cpython_files, graalpy_files):
        self.cpython_files = cpython_files
        self.graalpy_files = graalpy_files
        self.cpython_results = dict()
        self.graalpy_results = dict()

    def load(self):
        _load_and_extract_files(self.cpython_files, self.cpython_results)
        _load_and_extract_files(self.graalpy_files, self.graalpy_results)

    def save(self, output):
        packages = sorted(list(self.cpython_results.keys()))

        with open(output, "w", newline="") as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            spamwriter.writerow(
                [
                    "package",
                    "tests",
                    "cpython-passed",
                    "cpython-skipped",
                    "cpython-failed",
                    "cpython-error",
                    "graalpy-passed",
                    "graalpy-skipped",
                    "graalpy-failed",
                    "graalpy-error",
                ]
            )
            for package in packages:
                # Collect test results for both implementations
                cpython_result = self.cpython_results[package]
                graalpy_result = self.graalpy_results[package]
                # Check if at least one implementation has results
                haveResults = cpython_result.wasExecuted or graalpy_result.wasExecuted
                row = [package]

                if haveResults:
                    row.append(
                        cpython_result.tests
                        if cpython_result.wasExecuted
                        else graalpy_result.tests
                    )

                if cpython_result.wasExecuted:
                    row.extend(
                        [
                            cpython_result.passed,
                            cpython_result.skipped,
                            cpython_result.failures,
                            cpython_result.errors,
                        ]
                    )
                else:
                    row.extend(["", "", "", ""])

                if graalpy_result.wasExecuted:
                    row.extend(
                        [
                            graalpy_result.passed,
                            graalpy_result.skipped,
                            graalpy_result.failures,
                            graalpy_result.errors,
                        ]
                    )
                else:
                    row.extend(["", "", "", ""])
                spamwriter.writerow(row)
