"""
Custom Exceptions
"""


class WebsterError(
    Exception
):
    """
    Base Webster exception.
    """

    pass


class ServiceError(
    WebsterError
):
    """
    Service related error.
    """

    pass


class ConfigurationError(
    WebsterError
):
    """
    Configuration error.
    """

    pass


class PluginError(
    WebsterError
):
    """
    Plugin error.
    """

    pass


class AIError(
    WebsterError
):
    """
    AI related error.
    """

    pass