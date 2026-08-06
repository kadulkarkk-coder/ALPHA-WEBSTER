"""
Webster Alpha

Test Runner
"""

from __future__ import annotations

from core.tests.test_suite import TestSuite
from core.tests.test_status import TestStatus


class TestRunner:

    def __init__(
        self,
        suite: TestSuite
    ) -> None:

        self._suite = suite

    def run(self) -> bool:

        results = self._suite.run()

        print()

        print("=" * 60)

        print("WEBSTER ALPHA TEST REPORT")

        print("=" * 60)

        passed = 0

        failed = 0

        skipped = 0

        for result in results:

            print(

                f"[{result.status.value}] "

                f"{result.name}"

            )

            if result.message:

                print(

                    f"  {result.message}"

                )

            if result.status == TestStatus.PASSED:

                passed += 1

            elif result.status == TestStatus.FAILED:

                failed += 1

            else:

                skipped += 1

        print()

        print(f"Passed : {passed}")

        print(f"Failed : {failed}")

        print(f"Skipped: {skipped}")

        print()

        return failed == 0