"""
Workflow
"""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class Workflow:
    """
    Represents an automation workflow.
    """

    name: str

    enabled: bool = True

    workflow_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    actions: list[str] = field(
        default_factory=list
    )

    triggers: list[str] = field(
        default_factory=list
    )

    def add_action(
        self,
        action: str
    ) -> None:

        self.actions.append(
            action
        )

    def add_trigger(
        self,
        trigger: str
    ) -> None:

        self.triggers.append(
            trigger
        )