"""
System
"""

import platform


class System:
    """
    Webster system information.
    """

    @property
    def os(
        self
    ) -> str:

        return platform.system()

    @property
    def release(
        self
    ) -> str:

        return platform.release()

    @property
    def machine(
        self
    ) -> str:

        return platform.machine()

    @property
    def processor(
        self
    ) -> str:

        return platform.processor()

    @property
    def python(
        self
    ) -> str:

        return platform.python_version()