"""
Webster Alpha

Test Suite
"""

from __future__ import annotations

from core.tests.base_test import BaseTest


class TestSuite:

    def __init__(self) -> None:

        self._tests: list[BaseTest] = []

    def add(
        self,
        test: BaseTest
    ) -> None:

        self._tests.append(test)

    def run(self):

        return [

            test.execute()

            for test

            in self._tests

        ]

    @property
    def count(self) -> int:

        return len(self._tests)