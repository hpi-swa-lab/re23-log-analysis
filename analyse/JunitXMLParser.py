import xml.etree.ElementTree as ET

TESTSUITE_TAG = "testsuite"
TESTCASE_TAG = "testcase"
ERROR_TAG = "error"
FAILURE_TAG = "failure"


class JunitXMLParser(object):
    """
    Class to parse a JUnit XML file.
    You can extract the number of errors, failures and skipped tests and specific stacktraces.
    """

    def __init__(self, path):
        self.path = path
        self.root = ET.parse(path).getroot()

    def get_errors(self):
        errors = 0
        for testsuite in self.root.findall(TESTSUITE_TAG):
            errors += int(testsuite.attrib["errors"])
        return errors

    def get_failures(self):
        failures = 0
        for testsuite in self.root.findall(TESTSUITE_TAG):
            failures += int(testsuite.attrib["failures"])
        return failures

    def get_skipped(self):
        skipped = 0
        for testsuite in self.root.findall(TESTSUITE_TAG):
            skipped += int(testsuite.attrib["skipped"])
        return skipped

    def get_tests(self):
        tests = 0
        for testsuite in self.root.findall(TESTSUITE_TAG):
            tests += int(testsuite.attrib["tests"])
        return tests

    def get_error_stacktraces(self):
        return self._get_stacktraces(ERROR_TAG)

    def get_failure_stacktraces(self):
        return self._get_stacktraces(FAILURE_TAG)

    def _get_stacktraces(self, tag):
        stacktraces = []
        for testsuite in self.root.findall(TESTSUITE_TAG):
            for testcase in testsuite.findall(TESTCASE_TAG):
                class_name = testcase.attrib.get("classname", "UNKNOWN")
                name = testcase.attrib.get("name", "UNKNOWN")
                test_name = class_name + "." + name
                for failure in testcase.findall(tag):
                    message = failure.attrib.get("message", None)
                    error_type = failure.attrib.get("type", None)
                    trace = failure.text
                    stacktraces.append((test_name, error_type, message, trace))
        return stacktraces
