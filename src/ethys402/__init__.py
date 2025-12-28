"""ETHYS x402 Python SDK - Production-ready SDK for autonomous agents."""

from ethys402.client import AsyncEthysClient, EthysClient
from ethys402.errors import (
    ApiError,
    AuthError,
    EthysError,
    NetworkError,
    TimeoutError,
    ValidationError,
)
from ethys402.types import (
    AgentIdentity,
    ConnectRequest,
    ConnectResponse,
    DiscoverySearchResponse,
    InfoResponse,
    TelemetryEvent,
    TelemetryRequest,
    TrustAttestRequest,
    TrustScoreResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)

__version__ = "0.1.0"

__all__ = [
    # Clients
    "EthysClient",
    "AsyncEthysClient",
    # Errors
    "EthysError",
    "AuthError",
    "ValidationError",
    "ApiError",
    "NetworkError",
    "TimeoutError",
    # Types
    "AgentIdentity",
    "ConnectRequest",
    "ConnectResponse",
    "VerifyPaymentRequest",
    "VerifyPaymentResponse",
    "TelemetryRequest",
    "TelemetryEvent",
    "TrustScoreResponse",
    "TrustAttestRequest",
    "DiscoverySearchResponse",
    "InfoResponse",
]

