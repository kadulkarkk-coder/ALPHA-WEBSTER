"""Webster Alpha - Response Builder."""

from __future__ import annotations

from core.capability.result import CapabilityResult


class ResponseBuilder:
    """Converts execution results into concise user-facing responses."""

    def build(self, result: CapabilityResult) -> str:
        if result.success:
            return self._build_success(result)
        return self._build_failure(result)

    def _build_success(self, result: CapabilityResult) -> str:
        output = result.output
        if isinstance(output, str):
            return output or "Task completed successfully."

        if isinstance(output, list):
            if not output:
                return "Done. No matching items were found."
            lines = [f"Found {len(output)} item(s):"]
            for item in output:
                if isinstance(item, dict):
                    name = item.get("name", "item")
                    path = item.get("path")
                    kind = item.get("type")
                    suffix = f" — {path}" if path else ""
                    if kind:
                        lines.append(f"• {name} ({kind}){suffix}")
                    else:
                        lines.append(f"• {name}{suffix}")
                else:
                    lines.append(f"• {item}")
            return "\n".join(lines)

        if output is None:
            return "Task completed successfully."

        return f"Task completed successfully.\n\nResult:\n{output}"

    def _build_failure(self, result: CapabilityResult) -> str:
        if result.error:
            return f"Task failed.\n\nReason: {result.error}"
        return "The requested task could not be completed."

    def success(self, message: str) -> str:
        return message

    def error(self, message: str) -> str:
        return f"Error: {message}"

    def warning(self, message: str) -> str:
        return f"Warning: {message}"

    def info(self, message: str) -> str:
        return message

    def health(self) -> dict:
        return {"healthy": True, "builder": "ResponseBuilder"}

    def __repr__(self) -> str:
        return "ResponseBuilder()"
