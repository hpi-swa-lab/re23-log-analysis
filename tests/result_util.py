from __future__ import annotations

import os
from dataclasses import dataclass, KW_ONLY
from datetime import timedelta
from os import PathLike


@dataclass(frozen=True)
class TestResultCounts:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    unknown: int = 0

    def __post_init__(self):
        assert self.passed >= 0 and self.failed >= 0 and self.skipped >= 0 and self.unknown >= 0

    @classmethod
    def from_total(cls, total, failed, skipped=0, unknown=0):
        # n.b. the total printed by unittest sometimes doesn't add up
        passed = max(0, total - failed - skipped - unknown)
        return cls(passed, failed, skipped, unknown)

    @property
    def total(self):
        return self.passed + self.failed + self.skipped + self.unknown

    def __str__(self):
        return f"passed: {self.passed}, failed: {self.failed}, skipped: {self.skipped}, unknown: {self.unknown}"

    def __add__(self, other: TestResultCounts):
        if type(other) != type(self):
            return NotImplemented
        return TestResultCounts(
            passed=self.passed + other.passed,
            failed=self.failed + other.failed,
            skipped=self.skipped + other.skipped,
            unknown=self.unknown + other.unknown,
        )


@dataclass(kw_only=True)
class TestResult:
    name: str
    log_path: PathLike | str
    counts: TestResultCounts | None = None
    test_duration: timedelta | None = None
    installs: bool | None = None
    reference_impl: bool = False
    # Auxiliary results just provide additional logs/data, they don't affect the final aggregate result
    auxiliary: bool = False

    def as_dict(self) -> dict:
        result = {
            'name': self.name,
            'log_file': os.fspath(self.log_path),
        }
        if self.reference_impl:
            result['reference_impl'] = True
        if self.auxiliary:
            result['auxiliary'] = True
        if self.test_duration is not None:
            result['test_time'] = self.test_duration.total_seconds()
        if self.counts:
            result.update({
                'passed': self.counts.passed,
                'failed': self.counts.failed,
                'skipped': self.counts.skipped,
                'unknown': self.counts.unknown,
            })
        if self.installs is not None:
            result['installs'] = self.installs
        return result
