"""Tests for authentication and signing."""

import pytest
from eth_account import Account

from ethys402.auth import (
    create_agent_identity,
    get_agent_id_key,
    sign_connect_message,
    sign_telemetry_payload,
    verify_signature,
)
from ethys402.errors import AuthError, ValidationError
from ethys402.types import AgentIdentity


def test_sign_connect_message():
    """Test signing a connect message."""
    account = Account.create()
    address = account.address
    private_key = account.key.hex()

    message, signature = sign_connect_message(private_key, address)
    assert message == "Connect to ETHYS"
    assert signature.startswith("0x")
    assert len(signature) == 132

    # Verify signature
    assert verify_signature(address, message, signature)


def test_sign_connect_message_custom():
    """Test signing a custom connect message."""
    account = Account.create()
    address = account.address
    private_key = account.key.hex()

    custom_message = "Custom connect message"
    message, signature = sign_connect_message(private_key, address, custom_message)
    assert message == custom_message
    assert verify_signature(address, message, signature)


def test_sign_connect_message_wrong_address():
    """Test that wrong address raises error."""
    account = Account.create()
    private_key = account.key.hex()
    wrong_address = "0x" + "0" * 40

    with pytest.raises(AuthError):
        sign_connect_message(private_key, wrong_address)


def test_sign_telemetry_payload():
    """Test signing telemetry payload."""
    account = Account.create()
    address = account.address
    private_key = account.key.hex()

    agent_id = "agent_test123"
    timestamp = 1234567890
    nonce = "0x" + "a" * 64
    events = [{"type": "test", "timestamp": timestamp, "data": {}}]

    signature = sign_telemetry_payload(
        private_key, agent_id, address, timestamp, nonce, events
    )
    assert signature.startswith("0x")
    assert len(signature) == 132


def test_create_agent_identity_eoa():
    """Test creating EOA identity."""
    address = "0x" + "1" * 40
    identity = create_agent_identity(address)

    assert identity.version == 1
    assert identity.address == address
    assert identity.token_contract is None
    assert identity.token_id is None


def test_create_agent_identity_erc6551():
    """Test creating ERC-6551 identity."""
    address = "0x" + "1" * 40
    token_contract = "0x" + "2" * 40
    token_id = "123"

    identity = create_agent_identity(address, token_contract, token_id)

    assert identity.version == 1
    assert identity.address == address
    assert identity.token_contract == token_contract
    assert identity.token_id == token_id


def test_create_agent_identity_invalid_address():
    """Test that invalid address raises error."""
    with pytest.raises(ValidationError):
        create_agent_identity("invalid")


def test_get_agent_id_key():
    """Test deriving agent ID key."""
    address = "0x" + "1" * 40
    key = get_agent_id_key(address)

    assert key.startswith("0x")
    assert len(key) == 66  # 0x + 64 hex chars

    # Same address should produce same key
    key2 = get_agent_id_key(address)
    assert key == key2


def test_get_agent_id_key_erc6551():
    """Test deriving agent ID key for ERC-6551."""
    address = "0x" + "1" * 40
    token_contract = "0x" + "2" * 40
    token_id = "123"

    key1 = get_agent_id_key(address)
    key2 = get_agent_id_key(address, token_contract, token_id)

    # Different identities should produce different keys
    assert key1 != key2


def test_verify_signature():
    """Test signature verification."""
    account = Account.create()
    address = account.address
    private_key = account.key.hex()

    message = "Test message"
    _, signature = sign_connect_message(private_key, address, message)

    assert verify_signature(address, message, signature)
    assert not verify_signature(address, "Different message", signature)

    # Wrong address
    wrong_address = "0x" + "0" * 40
    assert not verify_signature(wrong_address, message, signature)

