"""
Configuration Loader
"""

import json
from pathlib import Path


class ConfigLoader:
    """
    Loads JSON configuration files.
    """

    def load(
        self,
        path: str | Path
    ) -> dict:

        path = Path(path)

        if not path.exists():

            raise FileNotFoundError(
                path
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)