"""Tests for client (mocked)."""

import pytest
from pytest_httpx import HTTPXMock

from ethys402.client import AsyncEthysClient, EthysClient
from ethys402.errors import ApiError, AuthError, ValidationError
from ethys402.types import TelemetryEvent


def test_get_info(httpx_mock: HTTPXMock):
    """Test get_info endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/info",
        json={
            "protocol": "x402",
            "name": "ETHYS x402 Protocol",
            "description": "Test",
            "version": "1.0.0",
            "onboarding": {"steps": []},
            "pricing": {"token": {}},
            "network": {"chainId": 8453},
            "endpoints": {},
            "features": [],
        },
    )

    client = EthysClient()
    info = client.get_info()

    assert info.protocol == "x402"
    assert info.name == "ETHYS x402 Protocol"
    client.close()


def test_connect(httpx_mock: HTTPXMock):
    """Test connect endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/connect",
        json={
            "success": True,
            "agentId": "agent_test123",
            "onboarding": {},
            "agentIdKey": "0x" + "a" * 64,
        },
    )

    client = EthysClient()
    response = client.connect(
        address="0x" + "1" * 40,
        signature="0x" + "a" * 130,
        message="Test message",
    )

    assert response.success
    assert response.agent_id == "agent_test123"
    client.close()


def test_verify_payment(httpx_mock: HTTPXMock):
    """Test verify_payment endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/verify-payment",
        json={
            "success": True,
            "agentId": "agent_test123",
            "activated": True,
            "apiKey": "test_api_key",
        },
    )

    client = EthysClient()
    response = client.verify_payment(
        agent_id="agent_test123",
        tx_hash="0x" + "1" * 64,
    )

    assert response.success
    assert response.activated
    client.close()


def test_telemetry(httpx_mock: HTTPXMock):
    """Test telemetry endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/telemetry",
        json={
            "success": True,
            "recorded": 1,
            "agentId": "agent_test123",
        },
    )

    from eth_account import Account

    account = Account.create()
    client = EthysClient()

    events = [
        TelemetryEvent(type="test", timestamp=1234567890, data={}),
    ]

    response = client.telemetry(
        agent_id="agent_test123",
        address=account.address,
        events=events,
        private_key=account.key.hex(),
    )

    assert response.success
    assert response.recorded == 1
    client.close()


def test_discovery_search(httpx_mock: HTTPXMock):
    """Test discovery_search endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/discovery/search?tags=nlp&minTrust=600",
        json={
            "success": True,
            "agents": [
                {
                    "agentId": "agent_test123",
                    "tags": ["nlp"],
                    "minTrust": 600,
                }
            ],
            "total": 1,
        },
    )

    client = EthysClient()
    response = client.discovery_search(tags="nlp", min_trust=600)

    assert response.success
    assert len(response.agents) == 1
    client.close()


def test_trust_score(httpx_mock: HTTPXMock):
    """Test trust_score endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/trust/score",
        json={
            "success": True,
            "agentId": "agent_test123",
            "trustScore": {"rs": 750, "ci": 0.85},
            "updatedAt": 1234567890,
        },
        match_headers={"Authorization": "Bearer test_key"},
    )

    client = EthysClient(api_key="test_key")
    response = client.trust_score()

    assert response.success
    assert response.trust_score["rs"] == 750
    client.close()


def test_error_handling_401(httpx_mock: HTTPXMock):
    """Test 401 error handling."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/trust/score",
        status_code=401,
        json={"error": "Unauthorized"},
    )

    client = EthysClient()
    with pytest.raises(AuthError):
        client.trust_score()
    client.close()


def test_error_handling_400(httpx_mock: HTTPXMock):
    """Test 400 error handling."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/connect",
        status_code=400,
        json={"error": "Invalid request"},
    )

    client = EthysClient()
    with pytest.raises(ValidationError):
        client.connect(
            address="invalid",
            signature="0x" + "a" * 130,
            message="Test",
        )
    client.close()


def test_error_handling_api_error(httpx_mock: HTTPXMock):
    """Test API error handling."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/info",
        status_code=500,
        json={"error": "Internal server error"},
    )

    client = EthysClient()
    with pytest.raises(ApiError) as exc_info:
        client.get_info()
    assert exc_info.value.status_code == 500
    client.close()


@pytest.mark.asyncio
async def test_async_get_info(httpx_mock: HTTPXMock):
    """Test async get_info endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/info",
        json={
            "protocol": "x402",
            "name": "ETHYS x402 Protocol",
            "description": "Test",
            "version": "1.0.0",
            "onboarding": {"steps": []},
            "pricing": {"token": {}},
            "network": {"chainId": 8453},
            "endpoints": {},
            "features": [],
        },
    )

    async with AsyncEthysClient() as client:
        info = await client.get_info()
        assert info.protocol == "x402"


@pytest.mark.asyncio
async def test_async_telemetry(httpx_mock: HTTPXMock):
    """Test async telemetry endpoint."""
    httpx_mock.add_response(
        url="https://402.ethys.dev/api/v1/402/telemetry",
        json={
            "success": True,
            "recorded": 1,
            "agentId": "agent_test123",
        },
    )

    from eth_account import Account

    account = Account.create()

    async with AsyncEthysClient() as client:
        events = [
            TelemetryEvent(type="test", timestamp=1234567890, data={}),
        ]

        response = await client.telemetry(
            agent_id="agent_test123",
            address=account.address,
            events=events,
            private_key=account.key.hex(),
        )

        assert response.success

