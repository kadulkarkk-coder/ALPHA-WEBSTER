"""
Extension Loader
"""

from importlib import import_module

from core.extensions.extension import Extension


class ExtensionLoader:
    """
    Dynamically loads Webster extensions.
    """

    def load(
        self,
        module_name: str,
        class_name: str
    ) -> Extension:

        module = import_module(
            module_name
        )

        extension_class = getattr(
            module,
            class_name
        )

        extension = extension_class()

        if not isinstance(
            extension,
            Extension
        ):

            raise TypeError(
                "Invalid extension type."
            )

        return extension