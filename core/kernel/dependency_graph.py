"""
Webster Alpha

Dependency Graph

Stateless dependency resolver.

The graph never stores components.

Instead, it analyses the Component Registry
whenever dependency information is needed.
"""

from __future__ import annotations

from collections import deque

from core.kernel.component_registry import (
    ComponentRegistry,
    ComponentRegistration,
)


class DependencyGraph:
    """
    Webster dependency resolver.
    """

    def __init__(
        self,
        registry: ComponentRegistry
    ) -> None:

        self._registry = registry

    #
    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    #

    def validate(
        self
    ) -> list[str]:

        errors: list[str] = []

        for registration in self._registry:

            info = registration.info

            for dependency in info.required_dependencies():

                if not self._registry.exists(

                    dependency.component

                ):

                    errors.append(

                        f"{info.name} requires "

                        f"{dependency.component}"

                    )

        return errors

    #
    # ---------------------------------------------------------
    # Startup Order
    # ---------------------------------------------------------
    #

    def startup_order(
        self
    ) -> list[
        ComponentRegistration
    ]:

        graph: dict[
            str,
            list[str]
        ] = {}

        indegree: dict[
            str,
            int
        ] = {}

        #
        # Build graph
        #

        for registration in self._registry:

            name = registration.name

            graph[name] = []

            indegree[name] = 0

        for registration in self._registry:

            info = registration.info

            for dependency in info.required_dependencies():

                graph[
                    dependency.component

                ].append(

                    info.name

                )

                indegree[
                    info.name

                ] += 1

        queue = deque(

            sorted(

                [

                    name

                    for name

                    in indegree

                    if indegree[name] == 0

                ],

                key=lambda name:

                self._registry

                .info(name)

                .priority

            )

        )

        result: list[
            ComponentRegistration
        ] = []

        while queue:

            current = queue.popleft()

            result.append(

                self._registry.registration(

                    current

                )

            )

            for child in graph[current]:

                indegree[child] -= 1

                if indegree[child] == 0:

                    queue.append(

                        child

                    )

        if len(result) != len(indegree):

            raise RuntimeError(

                "Circular dependency detected."

            )

        return result

    #
    # ---------------------------------------------------------
    # Shutdown Order
    # ---------------------------------------------------------
    #

    def shutdown_order(
        self
    ) -> list[
        ComponentRegistration
    ]:

        ordered = self.startup_order()

        ordered.reverse()

        return ordered

    #
    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------
    #

    def dependency_tree(
        self
    ) -> dict[
        str,
        list[str]
    ]:

        tree: dict[
            str,
            list[str]
        ] = {}

        for registration in self._registry:

            tree[
                registration.name

            ] = [

                dependency.component

                for dependency

                in registration

                .info

                .dependencies

            ]

        return tree

    def affected_components(
        self,
        component: str
    ) -> list[str]:

        affected: list[str] = []

        for registration in self._registry:

            if registration.info.has_dependency(

                component

            ):

                affected.append(

                    registration.name

                )

        return affected

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def count(
        self
    ) -> int:

        return self._registry.count

    def __repr__(
        self
    ) -> str:

        return (

            "DependencyGraph("

            f"components={self.count}"

            ")"

        )