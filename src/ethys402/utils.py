"""Utility functions for ETHYS x402 SDK."""

from typing import Any, Optional

from eth_utils import keccak, to_hex


def derive_agent_id_key(identity: "AgentIdentity") -> str:
    """
    Derive agentIdKey from AgentIdentity using keccak256.

    According to the spec:
    - agentIdKey = keccak256(abi.encode(AgentIdentity))
    - For EOA: version=1, address, tokenContract=0x0, tokenId=""
    - For ERC-6551: version=1, address, tokenContract, tokenId

    Args:
        identity: AgentIdentity structure

    Returns:
        Hex string (0x + 64 chars) representing the agentIdKey
    """
    # Import here to avoid circular dependency
    from ethys402.types import AgentIdentity  # noqa: F401

    # Build the encoded structure
    # Simplified encoding: version (uint8) + address (bytes20) + tokenContract (bytes20) + tokenId (bytes32)
    version_bytes = bytes([identity.version])
    address_bytes = bytes.fromhex(identity.address[2:])
    token_contract_bytes = (
        bytes.fromhex(identity.token_contract[2:]) if identity.token_contract else bytes(20)
    )
    token_id_bytes = (
        identity.token_id.encode("utf-8").ljust(32, b"\x00")
        if identity.token_id
        else bytes(32)
    )

    # Concatenate and hash
    encoded = version_bytes + address_bytes + token_contract_bytes + token_id_bytes
    agent_id_key = keccak(encoded)

    return to_hex(agent_id_key)


def generate_nonce() -> str:
    """
    Generate a 32-byte hex nonce for telemetry requests.

    Returns:
        Hex string (0x + 64 chars)
    """
    import secrets

    nonce_bytes = secrets.token_bytes(32)
    return to_hex(nonce_bytes)


def validate_address(address: str) -> bool:
    """
    Validate Ethereum address format.

    Args:
        address: Address string to validate

    Returns:
        True if valid, False otherwise
    """
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def validate_signature_format(signature: str) -> bool:
    """
    Validate signature format (0x + 130 hex chars).

    Args:
        signature: Signature string to validate

    Returns:
        True if valid, False otherwise
    """
    if not signature.startswith("0x"):
        return False
    if len(signature) != 132:  # 0x + 130 chars
        return False
    try:
        int(signature[2:], 16)
        return True
    except ValueError:
        return False


def build_telemetry_message(
    agent_id: str, address: str, timestamp: int, nonce: str, events: list[dict[str, Any]]
) -> str:
    """
    Build the message string for telemetry signature.

    According to the telemetry wallet auth guide, the message format is:
    "ETHYS Telemetry\nAgent: {agentId}\nAddress: {address}\nTimestamp: {ts}\nNonce: {nonce}\nEvents: {eventCount}"

    Args:
        agent_id: Agent ID
        address: Wallet address
        timestamp: Unix timestamp
        nonce: 32-byte hex nonce
        events: List of event dictionaries

    Returns:
        Message string to sign
    """
    event_count = len(events)
    return (
        f"ETHYS Telemetry\n"
        f"Agent: {agent_id}\n"
        f"Address: {address}\n"
        f"Timestamp: {timestamp}\n"
        f"Nonce: {nonce}\n"
        f"Events: {event_count}"
    )

