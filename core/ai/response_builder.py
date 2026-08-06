"""
Webster Alpha

Response Builder
"""

from __future__ import annotations

from core.capability.result import CapabilityResult
from core.capability.types import CapabilityResultStatus


class ResponseBuilder:
    """
    Converts internal execution results into
    user-friendly responses.
    """

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build(
        self,
        result: CapabilityResult,
    ) -> str:
        """
        Build a natural language response.
        """

        if result.success:

            return self._build_success(result)

        return self._build_failure(result)

    # ---------------------------------------------------------

    def _build_success(
        self,
        result: CapabilityResult,
    ) -> str:

        if isinstance(result.output, str):

            return result.output

        if result.output is None:

            return "Task completed successfully."

        return f"Task completed successfully.\n\nResult:\n{result.output}"

    # ---------------------------------------------------------

    def _build_failure(
        self,
        result: CapabilityResult,
    ) -> str:

        if result.error:

            return f"Task failed.\n\nReason: {result.error}"

        return "The requested task could not be completed."

    # ---------------------------------------------------------
    # Convenience Methods
    # ---------------------------------------------------------

    def success(
        self,
        message: str,
    ) -> str:

        return message

    # ---------------------------------------------------------

    def error(
        self,
        message: str,
    ) -> str:

        return f"Error: {message}"

    # ---------------------------------------------------------

    def warning(
        self,
        message: str,
    ) -> str:

        return f"Warning: {message}"

    # ---------------------------------------------------------

    def info(
        self,
        message: str,
    ) -> str:

        return message

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {

            "healthy": True,

            "builder": "ResponseBuilder",

        }

    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return "ResponseBuilder()"