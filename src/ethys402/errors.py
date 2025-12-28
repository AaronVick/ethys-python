"""Error hierarchy for ETHYS x402 SDK."""

from typing import Any, Optional


class EthysError(Exception):
    """Base exception for all ETHYS SDK errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NetworkError(EthysError):
    """Network-related errors (connection failures, DNS, etc.)."""

    pass


class TimeoutError(EthysError):
    """Request timeout errors."""

    pass


class AuthError(EthysError):
    """Authentication and authorization errors."""

    pass


class ValidationError(EthysError):
    """Request validation errors (missing fields, invalid format, etc.)."""

    pass


class ApiError(EthysError):
    """API errors with status codes and response bodies."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[dict[str, Any]] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body or {}

    def __str__(self) -> str:
        return f"{self.message} (status: {self.status_code})"

