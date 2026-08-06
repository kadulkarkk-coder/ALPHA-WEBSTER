"""
Plugin Manifest
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class PluginManifest:
    """
    Metadata describing a plugin.
    """

    name: str

    version: str

    author: str

    description: str

    entry: str

    dependencies: list[str] = field(
        default_factory=list
    )