"""
Validators
"""

from pathlib import Path


def not_empty(
    value: str
) -> bool:
    """
    Checks whether a string is empty.
    """

    return bool(
        value.strip()
    )


def file_exists(
    path: str
) -> bool:
    """
    Checks whether a file exists.
    """

    return Path(
        path
    ).exists()


def directory_exists(
    path: str
) -> bool:
    """
    Checks whether a directory exists.
    """

    return Path(
        path
    ).is_dir()


def positive(
    value: int | float
) -> bool:
    """
    Checks whether a number is positive.
    """

    return value > 0