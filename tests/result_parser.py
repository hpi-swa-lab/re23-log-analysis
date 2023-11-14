from __future__ import annotations

from os import PathLike

import operator
import re
from functools import reduce
from typing import Callable

from result_util import TestResultCounts

PARSERS = []

# Patterns that signify fatal crashes in the test framework and would better reject the whole result
REJECTED_PATTERNS = [
    re.compile(r'INTERNALERROR> Traceback \(most recent call last\):'),
]


def results_parser(fn: Callable[[str], TestResultCounts]):
    PARSERS.append(fn)
    return fn


@results_parser
def parse_pytest_results(test_log):
    matches = re.findall(r'^=+ ((?:\d+ (?:subtests )?\w+, )*\d+ (?:subtests )?\w+) in .+ =+$', test_log, re.MULTILINE)
    if not matches:
        return None
    passed = 0
    failed = 0
    skipped = 0
    unknown = 0
    for match in matches:
        for elem in match.split(', '):
            count, state = elem.split(' ', 1)
            count = int(count)
            if state in ('warning', 'warnings') or state.startswith('subtests '):
                continue
            if state == 'passed':
                passed += count
            elif state in ('failed', 'error', 'errors'):
                failed += count
            elif state in ('skipped', 'deselected', 'xfailed', 'xpassed'):
                skipped += count
            else:
                unknown += count

    return TestResultCounts(passed, failed, skipped, unknown)


@results_parser
def parse_pytest_sugar_results(test_log):
    if matches := re.findall(r'^Results \([^)]*\):\n((?:\s*\d+ \w+\n(?:\s+- .*\n)*)+)', test_log, re.MULTILINE):
        result = TestResultCounts()
        for match in matches:
            for line in match.splitlines():
                if submatch := re.match(r'\s*(\d+) (\w+)', line):
                    name = submatch.group(2)
                    value = int(submatch.group(1))
                    match name:
                        case 'passed':
                            result += TestResultCounts(passed=value)
                        case 'failed':
                            result += TestResultCounts(failed=value)
                        case 'skipped' | 'xfailed' | 'xpassed' | 'deselected':
                            result += TestResultCounts(skipped=value)
                        case _:
                            result += TestResultCounts(unknown=value)
        return result


@results_parser
def parse_zope_testrunner_results(test_log):
    matches = list(re.finditer(
        r'Ran (?P<total>\d+) tests with (?P<f>\d+) failures, (?P<e>\d+) errors, (?P<s>\d+) skipped in.*$',
        test_log,
        re.MULTILINE,
    ))
    if not matches:
        return None
    total = 0
    failures = 0
    skipped = 0
    for match in matches:
        total = total + int(match.group('total'))
        failures = failures + int(match.group('f')) + int(match.group('e'))
        skipped = skipped + int(match.group('s'))

    return TestResultCounts.from_total(total, failures, skipped, 0)


@results_parser
def parse_unittest_or_twisted_results(test_log):
    # unittest and twisted formats overlap, so we parse them together
    matches = re.findall(
        r'^Ran (\d+) tests? in .*\n\n(?:OK|PASSED|FAILED)(?: \(((?:[^=]+=\s*\d+,\s*)*[^=]+=\s*\d+)\))?',
        test_log,
        re.MULTILINE,
    )
    if not matches:
        return None
    total = 0
    passed = None
    failed = 0
    skipped = 0
    unknown = 0
    for total_str, rest in matches:
        total += int(total_str)
        if rest:
            for element in re.split(r',\s*', rest):
                element_match = element.split('=')
                name = element_match[0].strip()
                value = int(element_match[1].strip())
                if name == 'successes':
                    passed = (passed or 0) + value
                elif name in ('failures', 'errors'):
                    failed += value
                elif name in ('skipped', 'skips', 'expected failures'):
                    skipped += value
                else:
                    unknown += value
    if passed is None:
        return TestResultCounts.from_total(total, failed, skipped, unknown)
    else:
        return TestResultCounts(passed, failed, skipped, unknown)


@results_parser
def parse_stestr_results(test_log):
    matches = list(re.finditer(
        r'Ran: (?P<total>\d+) .*\n - Passed: (?P<p>\d+)\n - Skipped: (?P<s>\d+)\n - Expected Fail: (?P<ef>\d+)\n - Unexpected Success: (?P<us>\d+)\n - Failed: (?P<f>\d+)',
        test_log,
        re.MULTILINE,
    ))
    if not matches:
        return None
    passed = 0
    failed = 0
    skipped = 0
    for match in matches:
        passed = passed + int(match.group('p')) + int(match.group('ef'))
        skipped = skipped + int(match.group('s'))
        failed = failed + int(match.group('f')) + int(match.group('us'))

    return TestResultCounts(passed, failed, skipped)


@results_parser
def parse_pyyaml_results(test_log):
    matches = list(re.finditer(r'^(?P<state>(TESTS|FAILURES|ERRORS|Skipped)):?\s(?P<n>\d+).*$', test_log, re.MULTILINE))
    if not matches:
        return None
    total = 0
    failed = 0
    errors = 0
    skipped = 0
    for match in matches:
        state = match.group('state')
        n = match.group('n')
        if state == 'TESTS':
            total = int(n)
        elif state == 'FAILURES':
            failed = int(n)
        elif state == 'ERRORS':
            errors = int(n)
        elif state == 'Skipped':
            skipped += int(n)
    return TestResultCounts.from_total(total, failed + errors, skipped)


@results_parser
def parse_numpy_results(test_log):
    matches = re.findall(r'^((?:\d+ \w+, )*\d+ \w+) in .+\n_+ summary _+$', test_log, re.MULTILINE)
    if not matches:
        return None
    passed = 0
    failed = 0
    skipped = 0
    unknown = 0
    for match in matches:
        for elem in match.split(', '):
            count, state = elem.split(' ')
            count = int(count)
            if state in ('warning', 'warnings'):
                continue
            if state in ('passed', 'xpassed'):
                passed += count
            elif state == 'failed':
                failed += count
            elif state in ('skipped', 'xfailed'):
                skipped += count
            else:
                unknown += count

    return TestResultCounts(passed, failed, skipped, unknown)


def parse_junit_xml(xml_files: list[PathLike]):
    if xml_files:
        import junitparser, xml
        result = TestResultCounts()
        for xml_file in xml_files:
            try:
                parsed = junitparser.JUnitXml.fromfile(xml_file)
            except xml.etree.ElementTree.ParseError:
                result += TestResultCounts.from_total(total=0, failed=1)
            else:
                result += TestResultCounts.from_total(
                    parsed.tests,
                    parsed.failures + parsed.errors,
                    parsed.skipped,
                )
        return result


def parse_log(log_path: PathLike, strict: bool = True) -> TestResultCounts | None:
    with open(log_path, encoding='ascii', errors='replace') as test_log_file:
        test_log = test_log_file.read()
        # Remove ANSI control sequences
        test_log = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', test_log)
        if strict and any(p.search(test_log) for p in REJECTED_PATTERNS):
            return None
        results = []
        for parser in PARSERS:
            result = parser(test_log)
            if result is not None:
                results.append(result)

        if results:
            return reduce(operator.add, results)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('log_path')
    args = parser.parse_args()
    print(parse_log(args.log_path))
