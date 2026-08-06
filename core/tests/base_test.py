"""
Webster Alpha

Base Test
"""

from __future__ import annotations

import time

from abc import ABC
from abc import abstractmethod

from core.tests.test_result import TestResult
from core.tests.test_status import TestStatus


class BaseTest(ABC):

    def __init__(self) -> None:

        self.name = self.__class__.__name__

    def setup(self) -> None:

        pass

    @abstractmethod
    def run(self) -> None:
        ...

    def teardown(self) -> None:

        pass

    def execute(self) -> TestResult:

        start = time.perf_counter()

        try:

            self.setup()

            self.run()

            self.teardown()

            status = TestStatus.PASSED

            message = ""

        except Exception as exc:

            status = TestStatus.FAILED

            message = str(exc)

        duration = time.perf_counter() - start

        return TestResult(

            name=self.name,

            status=status,

            duration=duration,

            message=message

        )