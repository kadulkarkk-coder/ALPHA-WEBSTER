"""
Helpers
"""

from pathlib import Path
from datetime import datetime


def timestamp() -> str:
    """
    Current timestamp.
    """

    return datetime.now().isoformat()


def ensure_directory(
    path: str
) -> None:
    """
    Create directory if needed.
    """

    Path(
        path
    ).mkdir(
        parents=True,
        exist_ok=True
    )


def file_exists(
    path: str
) -> bool:
    """
    Check whether a file exists.
    """

    return Path(
        path
    ).exists()


def filename(
    path: str
) -> str:
    """
    Return filename.
    """

    return Path(
        path
    ).name