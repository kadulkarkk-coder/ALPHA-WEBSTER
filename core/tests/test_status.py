"""
Webster Alpha

Test Status
"""

from enum import Enum


class TestStatus(Enum):

    NOT_RUN = "NOT_RUN"

    RUNNING = "RUNNING"

    PASSED = "PASSED"

    FAILED = "FAILED"

    SKIPPED = "SKIPPED"

    ERROR = "ERROR"