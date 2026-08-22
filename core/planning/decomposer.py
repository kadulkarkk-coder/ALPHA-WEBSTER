"""Deterministic task decomposition for Webster goals."""

from __future__ import annotations

import re
from typing import List

from core.capability.registry import CapabilityRegistry
from .analyzer import GoalAnalysis
from .goal import Goal
from .task import Task


class TaskDecomposer:
    """Convert analyzed goals into executable tasks."""

    _SITE_ALIASES = {
        "google": "google.com",
        "youtube": "youtube.com",
        "github": "github.com",
        "facebook": "facebook.com",
        "instagram": "instagram.com",
        "twitter": "x.com",
        "x": "x.com",
        "reddit": "reddit.com",
        "wikipedia": "wikipedia.org",
        "amazon": "amazon.com",
        "gmail": "gmail.com",
        "google maps": "maps.google.com",
        "maps": "maps.google.com",
    }

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        self._registry = registry

    @property
    def registry(self) -> CapabilityRegistry | None:
        return self._registry

    def _available(self, capability: str) -> bool:
        return self._registry is None or self._registry.exists(capability)

    def create_task(self, goal: Goal, capability: str) -> Task:
        goal.validate()
        capability = capability.strip().lower()
        if not capability:
            raise ValueError("Capability name cannot be empty.")

        metadata: dict[str, object] = {"action": capability}
        if capability == "delete_file":
            metadata["requires_confirmation"] = True

        return Task(
            description=self._describe_task(goal.objective, capability),
            capability=capability,
            arguments=self._infer_arguments(goal.objective.strip(), capability),
            metadata=metadata,
        )

    def decompose(self, goal: Goal, analysis: GoalAnalysis | None = None) -> List[Task]:
        goal.validate()
        if analysis is None:
            from .analyzer import GoalAnalyzer
            analysis = GoalAnalyzer().analyze(goal)

        tasks: List[Task] = []
        for capability in analysis.required_capabilities:
            if not self._available(capability):
                continue
            tasks.append(self.create_task(goal, capability))
        return tasks

    def _describe_task(self, objective: str, capability: str) -> str:
        names = {
            "create_folder": "Create a folder", "create_file": "Create a file",
            "write_file": "Write file contents", "read_file": "Read a file",
            "rename_file": "Rename a file", "move_file": "Move a file",
            "copy_file": "Copy a file", "delete_file": "Delete a file",
            "list_directory": "List directory contents", "search_files": "Search filesystem entries",
            "open_url": "Open a URL", "refresh": "Refresh the browser",
            "browser_back": "Navigate browser back", "power": "Perform a system power action",
            "vision_enable": "Enable Webster vision", "vision_disable": "Disable Webster vision",
            "vision_status": "Check vision status", "vision_screen": "Capture and inspect the screen",
        }
        return f"{names.get(capability, capability)} for: {objective}"

    def _infer_arguments(self, objective: str, capability: str) -> dict[str, object]:
        text = objective.strip()
        lower = text.lower()

        if capability in {"vision_enable", "vision_disable", "vision_status", "vision_screen"}:
            return {}

        if capability in {"create_folder", "create_file"}:
            target = self._quoted_or_tail(text, ("called", "named"))
            if not target:
                marker = "folder" if capability == "create_folder" else "file"
                target = self._after_word(text, marker)
            if not target and capability == "create_file":
                match = re.search(r"\b(?:create|make)\s+(?:a\s+)?([^\s]+\.[a-z0-9]{1,8})\b", text, re.I)
                target = match.group(1) if match else None
            return {"path": target or ("NewFolder" if capability == "create_folder" else "new_file.txt")}

        if capability == "write_file":
            path = self._quoted_or_tail(text, ("file", "called", "named")) or "output.txt"
            content = self._extract_after(text, ("with content", "containing", "saying")) or ""
            return {"path": path, "content": content}

        if capability == "read_file":
            target = self._quoted_or_tail(text, ("file", "called", "named"))
            if not target:
                target = self._after_word(text, "file")
            if not target:
                match = re.search(r"\b(?:read|view|show|open)\s+(?:the\s+)?(.+?\.[a-z0-9]{1,8})\s*$", text, re.I)
                target = match.group(1).strip(" .\"'") if match else None
            return {"path": target or text}

        if capability == "rename_file":
            source, destination = self._extract_from_to(text)
            return {"source": source or text, "new_name": destination or "renamed_file"}

        if capability in {"move_file", "copy_file"}:
            source, destination = self._extract_from_to(text)
            return {"source": source or text, "destination": destination or "."}

        if capability == "delete_file":
            target = self._quoted_or_tail(text, ("file", "folder", "called", "named"))
            if not target:
                match = re.search(r"\b(?:delete|remove)\s+(?:the\s+)?(?:file\s+)?(.+?)(?:\s+confirmed)?\s*$", text, re.I)
                target = match.group(1).strip(" .\"'") if match else None
            return {"path": target or text, "require_confirmation": True, "confirmed": "confirmed" in lower}

        if capability == "list_directory":
            path = self._quoted_or_tail(text, ("in", "inside", "folder", "directory"))
            return {"path": path or "."}

        if capability == "search_files":
            return {"path": ".", "pattern": self._search_pattern(text), "recursive": True, "files_only": True}

        if capability == "open_url":
            match = re.search(r"(?:(?:https?://)|(?:www\.))[^\s]+", text, re.I)
            if match:
                url = match.group(0).rstrip(".,!?)]}")
            else:
                match = re.search(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", text, re.I)
                if match:
                    url = match.group(0).rstrip(".,!?)]}")
                else:
                    candidate = re.sub(r"^\s*(?:open|browse|visit|go to)\s+", "", text, flags=re.I).strip()
                    url = self._SITE_ALIASES.get(candidate.lower(), candidate.replace(" ", ""))
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            return {"url": url}

        if capability == "power":
            for action in ("shutdown", "restart", "sleep", "hibernate", "lock", "logout"):
                if action in lower:
                    return {"action": action}

        if capability == "browser_back":
            return {}

        return {}

    def _after_word(self, text: str, word: str) -> str | None:
        match = re.search(rf"\b{re.escape(word)}\b\s+(.+)$", text, re.I)
        return match.group(1).strip(" .\"'") if match else None

    def _extract_from_to(self, text: str) -> tuple[str | None, str | None]:
        match = re.search(r"(?:from\s+)?[\"']?(.+?)[\"']?\s+(?:to|into)\s+[\"']?(.+?)[\"']?$", text, re.I)
        if match:
            return match.group(1).strip(" .\"'"), match.group(2).strip(" .\"'")
        return None, None

    def _extract_after(self, text: str, markers: tuple[str, ...]) -> str | None:
        lower = text.lower()
        for marker in markers:
            index = lower.find(marker)
            if index >= 0:
                value = text[index + len(marker):].strip(" :.-\"")
                if value:
                    return value
        return None

    def _quoted_or_tail(self, text: str, markers: tuple[str, ...]) -> str | None:
        quoted = re.search(r"[\"']([^\"']+)[\"']", text)
        if quoted:
            return quoted.group(1).strip()
        lower = text.lower()
        for marker in markers:
            index = lower.find(marker.lower())
            if index >= 0:
                value = text[index + len(marker):].strip(" :.-")
                if value:
                    return value.split(" with content ", 1)[0].strip()
        return None

    def _search_pattern(self, text: str) -> str:
        match = re.search(r"\b(?:python|pdf|text|word|image|video|audio)\b", text, re.I)
        if match:
            return {"python": "*.py", "pdf": "*.pdf", "text": "*.txt", "word": "*.docx", "image": "*.png", "video": "*.mp4", "audio": "*.mp3"}[match.group(0).lower()]
        quoted = re.search(r"[\"']([^\"']+)[\"']", text)
        return quoted.group(1) if quoted else "*"
