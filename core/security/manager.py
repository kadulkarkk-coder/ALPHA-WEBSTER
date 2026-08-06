"""
Security Manager
"""

from core.security.crypto import Crypto
from core.security.vault import Vault
from core.security.security import SecurityContext


class SecurityManager:
    """
    Webster security controller.
    """

    def __init__(self) -> None:

        self._crypto = Crypto()

        self._vault = Vault()

        self._context = SecurityContext()

    @property
    def context(
        self
    ) -> SecurityContext:

        return self._context

    @property
    def vault(
        self
    ) -> Vault:

        return self._vault

    def authenticate(
        self
    ) -> None:

        self._context.authenticated = True

    def logout(
        self
    ) -> None:

        self._context.authenticated = False

    def hash(
        self,
        value: str
    ) -> str:

        return self._crypto.hash(
            value
        )

    def verify(
        self,
        value: str,
        hashed: str
    ) -> bool:

        return self._crypto.verify(
            value,
            hashed
        )