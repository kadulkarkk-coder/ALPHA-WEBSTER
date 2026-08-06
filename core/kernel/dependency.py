"""
Webster Alpha

Dependency System

Defines dependencies between Webster components.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from enum import Enum
from enum import auto


class DependencyType(
    Enum
):
    """
    Types of dependencies.
    """

    REQUIRED = auto()

    OPTIONAL = auto()

    BEFORE = auto()

    AFTER = auto()


@dataclass(slots=True)
class Dependency:
    """
    Represents a dependency on another component.
    """

    component: str

    dependency_type: DependencyType = (
        DependencyType.REQUIRED
    )

    description: str = ""

    version: str | None = None

    enabled: bool = True


@dataclass(slots=True)
class ComponentInfo:
    """
    Registration information for a component.
    """

    name: str

    priority: int = 100

    critical: bool = False

    startup_group: str = "default"

    dependencies: list[
        Dependency
    ] = field(
        default_factory=list
    )

    metadata: dict[
        str,
        str
    ] = field(
        default_factory=dict
    )

    #
    # ---------------------------------------------------------
    # Dependency Management
    # ---------------------------------------------------------
    #

    def add_dependency(
        self,
        component: str,
        dependency_type: DependencyType = (
            DependencyType.REQUIRED
        ),
        description: str = "",
        version: str | None = None
    ) -> None:

        self.dependencies.append(

            Dependency(

                component=component,

                dependency_type=dependency_type,

                description=description,

                version=version

            )

        )

    def remove_dependency(
        self,
        component: str
    ) -> None:

        self.dependencies = [

            dependency

            for dependency

            in self.dependencies

            if dependency.component != component

        ]

    def has_dependency(
        self,
        component: str
    ) -> bool:

        return any(

            dependency.component == component

            for dependency

            in self.dependencies

        )

    def required_dependencies(
        self
    ) -> list[
        Dependency
    ]:

        return [

            dependency

            for dependency

            in self.dependencies

            if (

                dependency.dependency_type

                ==

                DependencyType.REQUIRED

            )

        ]

    def optional_dependencies(
        self
    ) -> list[
        Dependency
    ]:

        return [

            dependency

            for dependency

            in self.dependencies

            if (

                dependency.dependency_type

                ==

                DependencyType.OPTIONAL

            )

        ]

    #
    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------
    #

    def set_metadata(
        self,
        key: str,
        value: str
    ) -> None:

        self.metadata[
            key
        ] = value

    def get_metadata(
        self,
        key: str,
        default: str = ""
    ) -> str:

        return self.metadata.get(

            key,

            default

        )

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "ComponentInfo("

            f"name='{self.name}', "

            f"dependencies={len(self.dependencies)}, "

            f"critical={self.critical}"

            ")"

        )