"""
Service Information
"""

from dataclasses import dataclass

from core.services.service_state import ServiceState


@dataclass(slots=True)
class ServiceInfo:
    """
    Metadata describing a service.
    """

    name: str

    version: str

    description: str

    state: ServiceState = ServiceState.CREATED