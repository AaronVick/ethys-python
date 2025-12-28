"""Type definitions for ETHYS x402 SDK using Pydantic v2."""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class AgentIdentity(BaseModel):
    """Agent identity structure (EOA or ERC-6551)."""

    version: int = Field(default=1, description="Identity version")
    address: str = Field(..., description="Wallet address (EOA) or ERC-6551 token-bound account")
    token_contract: Optional[str] = Field(
        default=None, alias="tokenContract", description="ERC-721 contract (ERC-6551 only)"
    )
    token_id: Optional[str] = Field(
        default=None, alias="tokenId", description="ERC-721 token ID (ERC-6551 only)"
    )

    @field_validator("address", "token_contract")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Address must be a valid Ethereum address (0x + 40 hex chars)")
        return v

    class Config:
        populate_by_name = True


class ConnectRequest(BaseModel):
    """Request to connect an agent."""

    address: str = Field(..., description="Wallet address")
    signature: str = Field(..., description="Wallet signature")
    message: str = Field(..., description="Signed message")
    token_contract: Optional[str] = Field(
        default=None, alias="tokenContract", description="ERC-721 contract (ERC-6551 only)"
    )
    token_id: Optional[str] = Field(
        default=None, alias="tokenId", description="ERC-721 token ID (ERC-6551 only)"
    )

    class Config:
        populate_by_name = True


class OnboardingStep(BaseModel):
    """Onboarding step information."""

    step: int
    title: str
    description: str
    endpoint: Optional[str] = None
    required: Optional[list[str]] = None


class PricingInfo(BaseModel):
    """Pricing information."""

    token: dict[str, Any]
    activation_fee: dict[str, Any] = Field(..., alias="activationFee")
    current_price_usd: Optional[float] = Field(None, alias="currentPriceUsd")
    token_amount: Optional[str] = Field(None, alias="tokenAmount")

    class Config:
        populate_by_name = True


class ConnectResponse(BaseModel):
    """Response from connect endpoint."""

    success: bool
    agent_id: str = Field(..., alias="agentId")
    onboarding: Optional[dict[str, Any]] = None
    policy: Optional[dict[str, Any]] = None
    agent_id_key: Optional[str] = Field(None, alias="agentIdKey")

    class Config:
        populate_by_name = True


class VerifyPaymentRequest(BaseModel):
    """Request to verify payment."""

    agent_id: str = Field(..., alias="agentId")
    tx_hash: str = Field(..., alias="txHash")

    class Config:
        populate_by_name = True


class VerifyPaymentResponse(BaseModel):
    """Response from verify-payment endpoint."""

    success: bool
    agent_id: str = Field(..., alias="agentId")
    api_key: Optional[str] = Field(None, alias="apiKey")
    activated: bool = False

    class Config:
        populate_by_name = True


class TelemetryEvent(BaseModel):
    """Single telemetry event."""

    type: str
    timestamp: int
    data: dict[str, Any] = Field(default_factory=dict)


class TelemetryRequest(BaseModel):
    """Telemetry submission request (wallet-signed)."""

    agent_id: str = Field(..., alias="agentId")
    address: str
    ts: int = Field(..., description="Unix timestamp")
    nonce: str = Field(..., description="32-byte hex nonce")
    events: list[TelemetryEvent]
    signature: str

    class Config:
        populate_by_name = True


class TelemetryResponse(BaseModel):
    """Response from telemetry endpoint."""

    success: bool
    recorded: int = 0
    agent_id: Optional[str] = Field(None, alias="agentId")

    class Config:
        populate_by_name = True


class TrustScoreResponse(BaseModel):
    """Trust score response."""

    success: bool
    agent_id: str = Field(..., alias="agentId")
    trust_score: dict[str, Any] = Field(..., alias="trustScore")
    updated_at: Optional[int] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True


class TrustAttestRequest(BaseModel):
    """Trust attestation request."""

    target_agent_id: str = Field(..., alias="targetAgentId")
    interaction_type: str = Field(..., alias="interactionType")
    rating: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        populate_by_name = True


class DiscoverySearchResponse(BaseModel):
    """Discovery search response."""

    success: bool
    agents: list[dict[str, Any]] = Field(default_factory=list)
    total: Optional[int] = None


class InfoResponse(BaseModel):
    """Response from /info endpoint."""

    protocol: str
    name: str
    description: str
    version: str
    onboarding: dict[str, Any]
    pricing: dict[str, Any]
    network: dict[str, Any]
    endpoints: dict[str, Any]
    features: list[str] = Field(default_factory=list)

