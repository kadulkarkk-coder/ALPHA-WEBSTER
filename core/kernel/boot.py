"""
Webster Alpha

Boot Manager

Coordinates Webster startup and shutdown.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Iterable

from core.kernel.component import Component
from core.kernel.lifecycle import Lifecycle


@dataclass(slots=True)
class BootReport:
    """
    Result of a boot sequence.
    """

    started: datetime

    finished: datetime | None = None

    initialized: list[str] = field(
        default_factory=list
    )

    started_components: list[str] = field(
        default_factory=list
    )

    failed: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    @property
    def success(
        self
    ) -> bool:

        return len(
            self.failed
        ) == 0

    @property
    def duration(
        self
    ) -> float:

        if self.finished is None:

            return 0.0

        return (

            self.finished

            -

            self.started

        ).total_seconds()


class Boot:
    """
    Webster boot coordinator.
    """

    def __init__(
        self,
        lifecycle: Lifecycle
    ) -> None:

        self._lifecycle = lifecycle

    #
    # ---------------------------------------------------------
    # Boot
    # ---------------------------------------------------------
    #

    def boot(
        self,
        components: Iterable[
            Component
        ]
    ) -> BootReport:

        report = BootReport(

            started=datetime.now()

        )

        #
        # Initialize
        #

        for component in components:

            if not component.enabled:

                report.warnings.append(

                    f"{component.name} disabled."

                )

                continue

            try:

                self._lifecycle.initialize(

                    component

                )

                report.initialized.append(

                    component.name

                )

            except Exception:

                report.failed.append(

                    component.name

                )

        #
        # Start
        #

        for component in components:

            if component.name in report.failed:

                continue

            if not component.enabled:

                continue

            try:

                self._lifecycle.start(

                    component

                )

                report.started_components.append(

                    component.name

                )

            except Exception:

                report.failed.append(

                    component.name

                )

        report.finished = datetime.now()

        return report

    #
    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------
    #

    def shutdown(
        self,
        components: Iterable[
            Component
        ]
    ) -> None:

        ordered = list(
            components
        )

        ordered.reverse()

        for component in ordered:

            try:

                self._lifecycle.stop(

                    component

                )

            except Exception:

                pass

            try:

                self._lifecycle.shutdown(

                    component

                )

            except Exception:

                pass