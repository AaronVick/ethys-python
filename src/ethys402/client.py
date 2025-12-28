"""Synchronous and asynchronous clients for ETHYS x402 SDK."""

import os
import time
from typing import Any, Optional

import httpx

from ethys402.auth import sign_connect_message, sign_telemetry_payload
from ethys402.errors import ApiError, AuthError, NetworkError, TimeoutError, ValidationError
from ethys402.types import (
    ConnectRequest,
    ConnectResponse,
    DiscoverySearchResponse,
    InfoResponse,
    TelemetryEvent,
    TelemetryRequest,
    TelemetryResponse,
    TrustAttestRequest,
    TrustScoreResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from ethys402.utils import generate_nonce


class BaseClient:
    """Base client with common functionality."""

    def __init__(
        self,
        base_url: str = "https://402.ethys.dev",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize base client.

        Args:
            base_url: Base URL for the API
            api_key: Optional API key for legacy authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("ETHYS_API_KEY")
        self.timeout = timeout

    def _get_headers(self, use_auth: bool = True) -> dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if use_auth and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle HTTP response and raise appropriate errors.

        Args:
            response: HTTP response

        Returns:
            Response JSON as dict

        Raises:
            NetworkError: For network issues
            TimeoutError: For timeout errors
            ApiError: For API errors with status codes
            ValidationError: For validation errors
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            try:
                error_body = e.response.json()
            except Exception:
                error_body = {"error": e.response.text or "Unknown error"}

            if status_code == 401:
                raise AuthError(
                    error_body.get("error", "Authentication failed"),
                    details=error_body,
                ) from e
            elif status_code == 400:
                raise ValidationError(
                    error_body.get("error", "Validation error"),
                    details=error_body,
                ) from e
            else:
                raise ApiError(
                    error_body.get("error", f"API error: {status_code}"),
                    status_code=status_code,
                    response_body=error_body,
                ) from e
        except httpx.TimeoutException as e:
            raise TimeoutError("Request timeout", details={"timeout": self.timeout}) from e
        except httpx.NetworkError as e:
            raise NetworkError("Network error", details={"error": str(e)}) from e

        try:
            return response.json()
        except Exception as e:
            raise ValidationError("Invalid JSON response", details={"error": str(e)}) from e


class EthysClient(BaseClient):
    """Synchronous client for ETHYS x402 API."""

    def __init__(
        self,
        base_url: str = "https://402.ethys.dev",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize synchronous client.

        Args:
            base_url: Base URL for the API
            api_key: Optional API key for legacy authentication
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, api_key, timeout)
        self._client = httpx.Client(timeout=self.timeout, base_url=self.base_url)

    def __enter__(self) -> "EthysClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def get_info(self) -> InfoResponse:
        """
        Get protocol information, pricing, and onboarding steps.

        Returns:
            InfoResponse with protocol details
        """
        response = self._client.get("/api/v1/402/info", headers=self._get_headers(use_auth=False))
        data = self._handle_response(response)
        return InfoResponse(**data)

    def connect(
        self,
        address: str,
        signature: str,
        message: str,
        token_contract: Optional[str] = None,
        token_id: Optional[str] = None,
    ) -> ConnectResponse:
        """
        Connect an agent with wallet signature.

        Args:
            address: Wallet address
            signature: Wallet signature
            message: Signed message
            token_contract: Optional ERC-721 contract (ERC-6551)
            token_id: Optional ERC-721 token ID (ERC-6551)

        Returns:
            ConnectResponse with agent ID and onboarding info
        """
        request = ConnectRequest(
            address=address,
            signature=signature,
            message=message,
            token_contract=token_contract,
            token_id=token_id,
        )
        response = self._client.post(
            "/api/v1/402/connect",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return ConnectResponse(**data)

    def connect_with_key(
        self, private_key: str, message: Optional[str] = None
    ) -> ConnectResponse:
        """
        Connect an agent using a private key (convenience method).

        Args:
            private_key: Hex-encoded private key
            message: Optional custom message

        Returns:
            ConnectResponse with agent ID and onboarding info
        """
        from eth_account import Account

        account = Account.from_key(private_key)
        address = account.address
        message, signature = sign_connect_message(private_key, address, message)
        return self.connect(address, signature, message)

    def verify_payment(
        self, agent_id: str, tx_hash: str
    ) -> VerifyPaymentResponse:
        """
        Verify payment transaction and activate agent.

        Args:
            agent_id: Agent ID from connect
            tx_hash: Transaction hash

        Returns:
            VerifyPaymentResponse with activation status
        """
        request = VerifyPaymentRequest(agent_id=agent_id, tx_hash=tx_hash)
        response = self._client.post(
            "/api/v1/402/verify-payment",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return VerifyPaymentResponse(**data)

    def telemetry(
        self,
        agent_id: str,
        address: str,
        events: list[TelemetryEvent],
        private_key: Optional[str] = None,
        timestamp: Optional[int] = None,
        nonce: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> TelemetryResponse:
        """
        Submit telemetry events (wallet-signed).

        Args:
            agent_id: Agent ID
            address: Wallet address
            events: List of telemetry events
            private_key: Private key for signing (if not providing signature)
            timestamp: Unix timestamp (defaults to current time)
            nonce: 32-byte hex nonce (auto-generated if not provided)
            signature: Pre-computed signature (if not using private_key)

        Returns:
            TelemetryResponse with recording status
        """
        if timestamp is None:
            timestamp = int(time.time())
        if nonce is None:
            nonce = generate_nonce()

        if signature is None:
            if private_key is None:
                raise ValidationError("Either private_key or signature must be provided")
            events_dict = [e.model_dump() for e in events]
            signature = sign_telemetry_payload(
                private_key, agent_id, address, timestamp, nonce, events_dict
            )

        request = TelemetryRequest(
            agent_id=agent_id,
            address=address,
            ts=timestamp,
            nonce=nonce,
            events=events,
            signature=signature,
        )
        response = self._client.post(
            "/api/v1/402/telemetry",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return TelemetryResponse(**data)

    def discovery_search(
        self,
        tags: Optional[str] = None,
        min_trust: Optional[int] = None,
        service_types: Optional[str] = None,
    ) -> DiscoverySearchResponse:
        """
        Search agents by capabilities and trust score.

        Args:
            tags: Comma-separated tags
            min_trust: Minimum trust score
            service_types: Comma-separated service types

        Returns:
            DiscoverySearchResponse with matching agents
        """
        params: dict[str, Any] = {}
        if tags:
            params["tags"] = tags
        if min_trust is not None:
            params["minTrust"] = min_trust
        if service_types:
            params["serviceTypes"] = service_types

        response = self._client.get(
            "/api/v1/402/discovery/search",
            params=params,
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return DiscoverySearchResponse(**data)

    def trust_score(self, agent_id: Optional[str] = None) -> TrustScoreResponse:
        """
        Get trust score for an agent.

        Args:
            agent_id: Optional agent ID (defaults to authenticated agent)

        Returns:
            TrustScoreResponse with trust score data
        """
        if agent_id:
            response = self._client.get(
                f"/api/v1/402/trust/score?agentId={agent_id}",
                headers=self._get_headers(),
            )
        else:
            response = self._client.get(
                "/api/v1/402/trust/score", headers=self._get_headers()
            )
        data = self._handle_response(response)
        return TrustScoreResponse(**data)

    def trust_attest(
        self,
        target_agent_id: str,
        interaction_type: str,
        rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Submit a trust attestation.

        Args:
            target_agent_id: Target agent ID
            interaction_type: Type of interaction
            rating: Optional rating (1-5)
            notes: Optional notes

        Returns:
            Response dict
        """
        request = TrustAttestRequest(
            target_agent_id=target_agent_id,
            interaction_type=interaction_type,
            rating=rating,
            notes=notes,
        )
        response = self._client.post(
            "/api/v1/402/trust/attest",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(),
        )
        return self._handle_response(response)

    def reviews_submit(
        self,
        target_agent_id: str,
        rating: int,
        review_text: str,
        signature: str,
        eip712_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Submit a client review (EIP-712 signed).

        Args:
            target_agent_id: Target agent ID
            rating: Rating (1-5)
            review_text: Review text
            signature: EIP-712 signature
            eip712_data: EIP-712 typed data

        Returns:
            Response dict
        """
        payload = {
            "targetAgentId": target_agent_id,
            "rating": rating,
            "reviewText": review_text,
            "signature": signature,
            "eip712": eip712_data,
        }
        response = self._client.post(
            "/api/v1/402/reviews/submit",
            json=payload,
            headers=self._get_headers(use_auth=False),
        )
        return self._handle_response(response)


class AsyncEthysClient(BaseClient):
    """Asynchronous client for ETHYS x402 API."""

    def __init__(
        self,
        base_url: str = "https://402.ethys.dev",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize asynchronous client.

        Args:
            base_url: Base URL for the API
            api_key: Optional API key for legacy authentication
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, api_key, timeout)
        self._client = httpx.AsyncClient(timeout=self.timeout, base_url=self.base_url)

    async def __aenter__(self) -> "AsyncEthysClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def get_info(self) -> InfoResponse:
        """Get protocol information, pricing, and onboarding steps."""
        response = await self._client.get(
            "/api/v1/402/info", headers=self._get_headers(use_auth=False)
        )
        data = self._handle_response(response)
        return InfoResponse(**data)

    async def connect(
        self,
        address: str,
        signature: str,
        message: str,
        token_contract: Optional[str] = None,
        token_id: Optional[str] = None,
    ) -> ConnectResponse:
        """Connect an agent with wallet signature."""
        request = ConnectRequest(
            address=address,
            signature=signature,
            message=message,
            token_contract=token_contract,
            token_id=token_id,
        )
        response = await self._client.post(
            "/api/v1/402/connect",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return ConnectResponse(**data)

    async def connect_with_key(
        self, private_key: str, message: Optional[str] = None
    ) -> ConnectResponse:
        """Connect an agent using a private key (convenience method)."""
        from eth_account import Account

        account = Account.from_key(private_key)
        address = account.address
        message, signature = sign_connect_message(private_key, address, message)
        return await self.connect(address, signature, message)

    async def verify_payment(
        self, agent_id: str, tx_hash: str
    ) -> VerifyPaymentResponse:
        """Verify payment transaction and activate agent."""
        request = VerifyPaymentRequest(agent_id=agent_id, tx_hash=tx_hash)
        response = await self._client.post(
            "/api/v1/402/verify-payment",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return VerifyPaymentResponse(**data)

    async def telemetry(
        self,
        agent_id: str,
        address: str,
        events: list[TelemetryEvent],
        private_key: Optional[str] = None,
        timestamp: Optional[int] = None,
        nonce: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> TelemetryResponse:
        """Submit telemetry events (wallet-signed)."""
        if timestamp is None:
            timestamp = int(time.time())
        if nonce is None:
            nonce = generate_nonce()

        if signature is None:
            if private_key is None:
                raise ValidationError("Either private_key or signature must be provided")
            events_dict = [e.model_dump() for e in events]
            signature = sign_telemetry_payload(
                private_key, agent_id, address, timestamp, nonce, events_dict
            )

        request = TelemetryRequest(
            agent_id=agent_id,
            address=address,
            ts=timestamp,
            nonce=nonce,
            events=events,
            signature=signature,
        )
        response = await self._client.post(
            "/api/v1/402/telemetry",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return TelemetryResponse(**data)

    async def discovery_search(
        self,
        tags: Optional[str] = None,
        min_trust: Optional[int] = None,
        service_types: Optional[str] = None,
    ) -> DiscoverySearchResponse:
        """Search agents by capabilities and trust score."""
        params: dict[str, Any] = {}
        if tags:
            params["tags"] = tags
        if min_trust is not None:
            params["minTrust"] = min_trust
        if service_types:
            params["serviceTypes"] = service_types

        response = await self._client.get(
            "/api/v1/402/discovery/search",
            params=params,
            headers=self._get_headers(use_auth=False),
        )
        data = self._handle_response(response)
        return DiscoverySearchResponse(**data)

    async def trust_score(self, agent_id: Optional[str] = None) -> TrustScoreResponse:
        """Get trust score for an agent."""
        if agent_id:
            response = await self._client.get(
                f"/api/v1/402/trust/score?agentId={agent_id}",
                headers=self._get_headers(),
            )
        else:
            response = await self._client.get(
                "/api/v1/402/trust/score", headers=self._get_headers()
            )
        data = self._handle_response(response)
        return TrustScoreResponse(**data)

    async def trust_attest(
        self,
        target_agent_id: str,
        interaction_type: str,
        rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """Submit a trust attestation."""
        request = TrustAttestRequest(
            target_agent_id=target_agent_id,
            interaction_type=interaction_type,
            rating=rating,
            notes=notes,
        )
        response = await self._client.post(
            "/api/v1/402/trust/attest",
            json=request.model_dump(by_alias=True),
            headers=self._get_headers(),
        )
        return self._handle_response(response)

    async def reviews_submit(
        self,
        target_agent_id: str,
        rating: int,
        review_text: str,
        signature: str,
        eip712_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Submit a client review (EIP-712 signed)."""
        payload = {
            "targetAgentId": target_agent_id,
            "rating": rating,
            "reviewText": review_text,
            "signature": signature,
            "eip712": eip712_data,
        }
        response = await self._client.post(
            "/api/v1/402/reviews/submit",
            json=payload,
            headers=self._get_headers(use_auth=False),
        )
        return self._handle_response(response)

