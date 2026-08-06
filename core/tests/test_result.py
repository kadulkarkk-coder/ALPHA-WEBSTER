"""
Webster Alpha

Test Result
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.tests.test_status import TestStatus


@dataclass(slots=True)
class TestResult:

    name: str

    status: TestStatus

    duration: float

    message: str = ""

    timestamp: datetime = datetime.now()