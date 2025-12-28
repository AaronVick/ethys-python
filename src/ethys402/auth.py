"""Authentication and signing utilities for ETHYS x402 SDK."""

from typing import Optional

from eth_account import Account, messages
from eth_account.signers.local import LocalAccount

from ethys402.errors import AuthError, ValidationError
from ethys402.types import AgentIdentity
from ethys402.utils import (
    build_telemetry_message,
    derive_agent_id_key,
    generate_nonce,
    validate_address,
    validate_signature_format,
)


def sign_connect_message(
    private_key: str, address: str, message: Optional[str] = None
) -> tuple[str, str]:
    """
    Sign a message for the /connect endpoint.

    Args:
        private_key: Hex-encoded private key (with or without 0x prefix)
        address: Wallet address (must match private key)
        message: Optional custom message (defaults to "Connect to ETHYS")

    Returns:
        Tuple of (message, signature)
    """
    if not validate_address(address):
        raise ValidationError("Invalid address format")

    account = Account.from_key(private_key)
    if account.address.lower() != address.lower():
        raise AuthError("Address does not match private key")

    if message is None:
        message = "Connect to ETHYS"

    message_obj = messages.encode_defunct(text=message)
    signed = account.sign_message(message_obj)

    return message, signed.signature.hex()


def sign_telemetry_payload(
    private_key: str,
    agent_id: str,
    address: str,
    timestamp: int,
    nonce: str,
    events: list[dict],
) -> str:
    """
    Sign a telemetry payload for the /telemetry endpoint.

    Args:
        private_key: Hex-encoded private key
        agent_id: Agent ID
        address: Wallet address
        timestamp: Unix timestamp
        nonce: 32-byte hex nonce
        events: List of event dictionaries

    Returns:
        Hex-encoded signature
    """
    account = Account.from_key(private_key)
    if account.address.lower() != address.lower():
        raise AuthError("Address does not match private key")

    message = build_telemetry_message(agent_id, address, timestamp, nonce, events)
    message_obj = messages.encode_defunct(text=message)
    signed = account.sign_message(message_obj)

    return signed.signature.hex()


def verify_signature(address: str, message: str, signature: str) -> bool:
    """
    Verify an Ethereum signature.

    Args:
        address: Expected signer address
        message: Original message
        signature: Hex-encoded signature

    Returns:
        True if signature is valid, False otherwise
    """
    if not validate_address(address):
        return False
    if not validate_signature_format(signature):
        return False

    try:
        message_obj = messages.encode_defunct(text=message)
        recovered = Account.recover_message(message_obj, signature=signature)
        return recovered.lower() == address.lower()
    except Exception:
        return False


def create_agent_identity(
    address: str, token_contract: Optional[str] = None, token_id: Optional[str] = None
) -> AgentIdentity:
    """
    Create an AgentIdentity structure.

    Args:
        address: Wallet address (EOA) or ERC-6551 token-bound account address
        token_contract: ERC-721 contract address (for ERC-6551)
        token_id: ERC-721 token ID (for ERC-6551)

    Returns:
        AgentIdentity instance
    """
    if not validate_address(address):
        raise ValidationError("Invalid address format")

    if token_contract and not validate_address(token_contract):
        raise ValidationError("Invalid token contract address format")

    return AgentIdentity(
        version=1,
        address=address,
        token_contract=token_contract,
        token_id=token_id,
    )


def get_agent_id_key(
    address: str, token_contract: Optional[str] = None, token_id: Optional[str] = None
) -> str:
    """
    Get the agentIdKey for an identity.

    Args:
        address: Wallet address
        token_contract: Optional ERC-721 contract (ERC-6551)
        token_id: Optional ERC-721 token ID (ERC-6551)

    Returns:
        Hex-encoded agentIdKey (0x + 64 chars)
    """
    identity = create_agent_identity(address, token_contract, token_id)
    return derive_agent_id_key(identity)

