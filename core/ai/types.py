"""
Webster Alpha

AI Types
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class AIProvider(Enum):
    """
    Supported AI providers.
    """

    WEBSTER = auto()

    GEMINI = auto()

    OPENAI = auto()

    CLAUDE = auto()

    OLLAMA = auto()

    LLAMA = auto()

    MISTRAL = auto()

    CUSTOM = auto()


class AIStatus(Enum):
    """
    Provider state.
    """

    OFFLINE = auto()

    INITIALIZING = auto()

    READY = auto()

    BUSY = auto()

    ERROR = auto()


class ResponseMode(Enum):
    """
    Desired response behavior.
    """

    CHAT = auto()

    COMMAND = auto()

    REASONING = auto()

    ANALYSIS = auto()

    CODE = auto()

    CREATIVE = auto()

    VISION = auto()

    PLANNING = auto()


class AIModelType(Enum):
    """
    General model capability.
    """

    LANGUAGE = auto()

    VISION = auto()

    MULTIMODAL = auto()

    EMBEDDING = auto()

    SPEECH = auto()

    REASONING = auto()