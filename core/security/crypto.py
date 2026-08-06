"""
Encryption Utilities
"""

import hashlib


class Crypto:
    """
    Provides hashing utilities.
    """

    def hash(
        self,
        value: str
    ) -> str:

        return hashlib.sha256(
            value.encode(
                "utf-8"
            )
        ).hexdigest()

    def verify(
        self,
        value: str,
        hashed: str
    ) -> bool:

        return self.hash(
            value
        ) == hashed