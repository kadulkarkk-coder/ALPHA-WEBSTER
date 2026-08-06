"""
Configuration Profile
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ConfigProfile:
    """
    Active Webster configuration profile.
    """

    name: str = "default"

    debug: bool = False

    autosave: bool = True

    theme: str = "system"

    language: str = "en"

    environment: str = "production"