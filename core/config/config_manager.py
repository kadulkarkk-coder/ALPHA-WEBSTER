"""
Configuration Manager
"""

from pathlib import Path

from core.config.config_loader import ConfigLoader
from core.config.config_validator import ConfigValidator
from core.config.config_profile import ConfigProfile


class ConfigManager:
    """
    Webster configuration manager.
    """

    def __init__(self) -> None:

        self._profile = ConfigProfile()

        self._loader = ConfigLoader()

        self._validator = ConfigValidator()

        self._config: dict = {}

    @property
    def profile(self) -> ConfigProfile:

        return self._profile

    @property
    def loaded(self) -> bool:

        return bool(
            self._config
        )

    def load(
        self,
        path: str | Path
    ) -> None:

        config = self._loader.load(
            path
        )

        self._validator.validate(
            config
        )

        self._config = config

        self._profile.name = config.get(
            "profile",
            "default"
        )

        self._profile.debug = config.get(
            "debug",
            False
        )

    def get(
        self,
        key: str,
        default=None
    ):

        return self._config.get(
            key,
            default
        )

    def set(
        self,
        key: str,
        value
    ) -> None:

        self._config[key] = value

    def all(self) -> dict:

        return self._config.copy()