"""Tests for utility functions."""

import pytest

from ethys402.utils import (
    build_telemetry_message,
    derive_agent_id_key,
    generate_nonce,
    validate_address,
    validate_signature_format,
)
from ethys402.types import AgentIdentity


def test_validate_address():
    """Test address validation."""
    assert validate_address("0x" + "1" * 40)
    assert not validate_address("0x" + "1" * 39)  # Too short
    assert not validate_address("1" * 40)  # Missing 0x
    assert not validate_address("0x" + "g" * 40)  # Invalid hex
    assert not validate_address("")


def test_validate_signature_format():
    """Test signature format validation."""
    assert validate_signature_format("0x" + "1" * 130)
    assert not validate_signature_format("0x" + "1" * 129)  # Too short
    assert not validate_signature_format("1" * 130)  # Missing 0x
    assert not validate_signature_format("0x" + "g" * 130)  # Invalid hex


def test_generate_nonce():
    """Test nonce generation."""
    nonce1 = generate_nonce()
    nonce2 = generate_nonce()

    assert nonce1.startswith("0x")
    assert len(nonce1) == 66  # 0x + 64 hex chars
    assert nonce1 != nonce2  # Should be unique


def test_build_telemetry_message():
    """Test telemetry message construction."""
    agent_id = "agent_test123"
    address = "0x" + "1" * 40
    timestamp = 1234567890
    nonce = "0x" + "a" * 64
    events = [
        {"type": "event1", "timestamp": timestamp, "data": {}},
        {"type": "event2", "timestamp": timestamp, "data": {}},
    ]

    message = build_telemetry_message(agent_id, address, timestamp, nonce, events)

    assert "ETHYS Telemetry" in message
    assert agent_id in message
    assert address in message
    assert str(timestamp) in message
    assert nonce in message
    assert "Events: 2" in message


def test_derive_agent_id_key_eoa():
    """Test agent ID key derivation for EOA."""
    identity = AgentIdentity(
        version=1,
        address="0x" + "1" * 40,
        token_contract=None,
        token_id=None,
    )

    key = derive_agent_id_key(identity)
    assert key.startswith("0x")
    assert len(key) == 66

    # Same identity should produce same key
    key2 = derive_agent_id_key(identity)
    assert key == key2


def test_derive_agent_id_key_erc6551():
    """Test agent ID key derivation for ERC-6551."""
    identity = AgentIdentity(
        version=1,
        address="0x" + "1" * 40,
        token_contract="0x" + "2" * 40,
        token_id="123",
    )

    key = derive_agent_id_key(identity)
    assert key.startswith("0x")
    assert len(key) == 66

    # Different identity should produce different key
    identity2 = AgentIdentity(
        version=1,
        address="0x" + "1" * 40,
        token_contract=None,
        token_id=None,
    )
    key2 = derive_agent_id_key(identity2)
    assert key != key2

