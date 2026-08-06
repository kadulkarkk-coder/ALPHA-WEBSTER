"""core.planning.decomposer

Deterministic TaskDecomposer to convert a Goal + GoalAnalysis into Tasks.
"""
from __future__ import annotations

from typing import List

from .goal import Goal
from .analyzer import GoalAnalysis
from .task import Task


class TaskDecomposer:
    """
    Deterministic decomposer. Extensible rule set.
    """

    def decompose(self, goal: Goal, analysis: GoalAnalysis | None = None) -> List[Task]:
        goal.validate()

        text = goal.objective.strip()

        if analysis is None:
            from .analyzer import GoalAnalyzer

            analysis = GoalAnalyzer().analyze(goal)

        tasks: List[Task] = []

        for capability in analysis.required_capabilities:
            arguments = self._infer_arguments(text, capability)
            description = self._describe_task(text, capability)
            tasks.append(Task(description=description, capability=capability, arguments=arguments))

        if not tasks:
            tasks.append(Task(description=goal.objective, capability="open_url", arguments={"url": text}))

        return tasks

    # ---------------------------------------------------------

    def _describe_task(self, objective: str, capability: str) -> str:
        if capability == "create_folder":
            return f"Create a folder for: {objective}"
        if capability == "write_file":
            return f"Create or write a file for: {objective}"
        if capability == "read_file":
            return f"Read a file for: {objective}"
        if capability == "list_directory":
            return f"List directory contents for: {objective}"
        if capability == "search":
            return f"Search files for: {objective}"
        if capability == "open_url":
            return f"Open a URL or website for: {objective}"
        if capability == "web_search":
            return f"Search the web for: {objective}"
        if capability == "refresh":
            return f"Refresh the browser for: {objective}"
        if capability == "back":
            return f"Navigate browser back for: {objective}"
        if capability == "forward":
            return f"Navigate browser forward for: {objective}"
        if capability == "close_tab":
            return f"Close a browser tab for: {objective}"
        if capability == "power":
            return f"Perform system power action for: {objective}"
        if capability == "launch_application":
            return f"Launch an application for: {objective}"
        if capability == "kill_process":
            return f"Terminate a process for: {objective}"
        return f"Execute capability '{capability}' for: {objective}"

    def _infer_arguments(self, objective: str, capability: str) -> dict[str, object]:
        objective_lower = objective.lower()

        if capability == "create_folder":
            path = self._extract_target_name(objective, ["called", "named", "folder", "directory"])
            if path:
                return {"path": path}

        if capability == "write_file":
            filename = self._extract_target_name(objective, ["called", "named", "file"])
            if filename:
                return {"path": filename, "content": ""}

        if capability == "read_file":
            path = self._extract_target_name(objective, ["called", "named", "file"])
            if path:
                return {"path": path}

        if capability == "list_directory":
            path = self._extract_target_name(objective, ["in", "folder", "directory"])
            if path:
                return {"path": path}

        if capability == "search":
            query = self._extract_target_name(objective, ["for", "named", "called"])
            if query:
                return {"query": query, "path": "."}

        if capability == "open_url":
            if "chatgpt" in objective_lower:
                return {"url": "https://chat.openai.com"}
            if "http" in objective_lower or "www." in objective_lower:
                for token in objective.split():
                    if token.startswith("http") or token.startswith("www."):
                        return {"url": token}
            query = self._extract_target_name(objective, ["for", "to", "open"])
            if query:
                return {"url": query}

        if capability == "web_search":
            query = self._extract_target_name(objective, ["for", "about", "search"])
            return {"query": query or objective}

        if capability == "power":
            if "shutdown" in objective_lower:
                return {"action": "shutdown"}
            if "restart" in objective_lower:
                return {"action": "restart"}
            if "sleep" in objective_lower or "hibernate" in objective_lower:
                return {"action": "sleep"}
            if "lock" in objective_lower:
                return {"action": "lock"}
            if "logout" in objective_lower:
                return {"action": "logout"}

        if capability == "launch_application":
            app_name = self._extract_target_name(objective, ["open", "launch", "start", "run"])
            if app_name:
                return {"application": app_name}

        if capability == "kill_process":
            process_name = self._extract_target_name(objective, ["process", "application", "app", "named"])
            if process_name:
                return {"process_name": process_name}

        return {}

    def _extract_target_name(self, objective: str, markers: list[str]) -> str | None:
        lower = objective.lower()

        for marker in markers:
            if marker in lower:
                parts = lower.split(marker, 1)[1].strip()
                if not parts:
                    continue
                if parts.startswith("named "):
                    parts = parts[len("named "):]
                if parts.startswith("called "):
                    parts = parts[len("called "):]
                parts = parts.strip(" .")
                tokens = parts.split()
                if tokens:
                    return tokens[0]
        return None
