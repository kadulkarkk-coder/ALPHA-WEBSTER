"""
Webster Alpha

Conversation History
"""

from __future__ import annotations

from collections.abc import Iterator

from core.messaging.message import Message


class ConversationHistory:
    """
    Stores the chronological message history
    for a conversation.
    """

    def __init__(self) -> None:

        self._messages: list[Message] = []

    #
    # ---------------------------------------------------------
    # Modification
    # ---------------------------------------------------------
    #

    def append(
        self,
        message: Message
    ) -> None:

        self._messages.append(message)

    def clear(
        self
    ) -> None:

        self._messages.clear()

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    def all(
        self
    ) -> list[Message]:

        return self._messages.copy()

    def latest(
        self
    ) -> Message | None:

        if not self._messages:

            return None

        return self._messages[-1]

    def last(
        self,
        count: int
    ) -> list[Message]:

        if count <= 0:

            return []

        return self._messages[-count:]

    #
    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------
    #

    def search(
        self,
        text: str,
        case_sensitive: bool = False
    ) -> list[Message]:

        results: list[Message] = []

        search = text

        if not case_sensitive:

            search = search.lower()

        for message in self._messages:

            content = message.content

            if not case_sensitive:

                content = content.lower()

            if search in content:

                results.append(message)

        return results

    #
    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    #

    @property
    def count(
        self
    ) -> int:

        return len(self._messages)

    @property
    def empty(
        self
    ) -> bool:

        return not self._messages

    #
    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------
    #

    def __len__(
        self
    ) -> int:

        return self.count

    def __iter__(
        self
    ) -> Iterator[Message]:

        return iter(self._messages)

    def __repr__(
        self
    ) -> str:

        return (

            "ConversationHistory("

            f"messages={self.count}"

            ")"

        )