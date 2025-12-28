"""Tests for type models."""

import pytest

from ethys402.types import (
    AgentIdentity,
    ConnectRequest,
    TelemetryEvent,
    TelemetryRequest,
    TrustAttestRequest,
)


def test_agent_identity_eoa():
    """Test EOA identity model."""
    identity = AgentIdentity(
        version=1,
        address="0x" + "1" * 40,
    )

    assert identity.version == 1
    assert identity.token_contract is None
    assert identity.token_id is None


def test_agent_identity_erc6551():
    """Test ERC-6551 identity model."""
    identity = AgentIdentity(
        version=1,
        address="0x" + "1" * 40,
        token_contract="0x" + "2" * 40,
        token_id="123",
    )

    assert identity.token_contract == "0x" + "2" * 40
    assert identity.token_id == "123"


def test_agent_identity_validation():
    """Test address validation."""
    with pytest.raises(ValueError):
        AgentIdentity(address="invalid")

    with pytest.raises(ValueError):
        AgentIdentity(
            address="0x" + "1" * 40,
            token_contract="invalid",
        )


def test_connect_request():
    """Test connect request model."""
    request = ConnectRequest(
        address="0x" + "1" * 40,
        signature="0x" + "a" * 130,
        message="Test message",
    )

    assert request.address == "0x" + "1" * 40
    assert request.message == "Test message"

    # Test alias
    data = request.model_dump(by_alias=True)
    assert "address" in data
    assert "signature" in data


def test_telemetry_event():
    """Test telemetry event model."""
    event = TelemetryEvent(
        type="test",
        timestamp=1234567890,
        data={"key": "value"},
    )

    assert event.type == "test"
    assert event.timestamp == 1234567890
    assert event.data == {"key": "value"}


def test_telemetry_request():
    """Test telemetry request model."""
    events = [
        TelemetryEvent(type="test", timestamp=1234567890, data={}),
    ]

    request = TelemetryRequest(
        agent_id="agent_test123",
        address="0x" + "1" * 40,
        ts=1234567890,
        nonce="0x" + "a" * 64,
        events=events,
        signature="0x" + "b" * 130,
    )

    assert request.agent_id == "agent_test123"
    assert len(request.events) == 1

    # Test alias
    data = request.model_dump(by_alias=True)
    assert "agentId" in data
    assert "ts" in data


def test_trust_attest_request():
    """Test trust attest request model."""
    request = TrustAttestRequest(
        target_agent_id="agent_target",
        interaction_type="test",
        rating=5,
        notes="Great agent",
    )

    assert request.target_agent_id == "agent_target"
    assert request.rating == 5

    # Test alias
    data = request.model_dump(by_alias=True)
    assert "targetAgentId" in data
    assert "interactionType" in data

