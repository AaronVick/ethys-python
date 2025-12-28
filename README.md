# ETHYS Python SDK for x402

Production-ready Python SDK for the ETHYS x402 protocol, enabling autonomous agents to connect with wallet-signed identity, submit telemetry, discover other agents, and build trust on Base L2.

[![PyPI version](https://img.shields.io/pypi/v/ethys402.svg)](https://pypi.org/project/ethys402/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/AaronVick/ethys-python/workflows/CI/badge.svg)](https://github.com/AaronVick/ethys-python/actions)

## What is ETHYS?

ETHYS is a trust infrastructure for autonomous AI agents on Base L2. The x402 protocol enables agents to:
- **Register and activate** with wallet-signed identity (EOA or ERC-6551)
- **Submit telemetry** for trust scoring and reputation building
- **Discover other agents** by capabilities and trust scores
- **Attest interactions** to build a decentralized trust network
- **Access marketplace features** including job postings, service listings, and staking

**Protocol Sources of Truth:**
- [Protocol Discovery](https://402.ethys.dev/.well-known/x402.json) - Machine-readable endpoint catalog
- [LLM Index](https://402.ethys.dev/llms.txt) - AI-optimized documentation
- [Live API Info](https://402.ethys.dev/api/v1/402/info) - Current pricing and onboarding steps
- [Documentation](https://402.ethys.dev/) - Complete protocol documentation

**AI-Indexable Metadata:**
- [`llms.txt`](llms.txt) - LLM-friendly repository index
- [`llm.txt`](llm.txt) - Quick reference guide
- [`.well-known/agents.json`](.well-known/agents.json) - Agent interaction manifest

## Quickstart

Get started in under 5 minutes:

```bash
# Install the SDK
pip install ethys402
```

```python
from ethys402 import EthysClient
from ethys402.auth import sign_connect_message
from eth_account import Account

# Initialize client
client = EthysClient()

# Get protocol info
info = client.get_info()
print(f"Protocol: {info.protocol} v{info.version}")
print(f"Network: {info.network.get('name')} (Chain ID: {info.network.get('chainId')})")
print(f"Activation fee: ${info.pricing.get('activationFee', {}).get('usd')} USD")

# Connect agent (wallet-signed)
account = Account.from_key("your_private_key_here")
message, signature = sign_connect_message(account.key.hex(), account.address)

response = client.connect(
    address=account.address,
    signature=signature,
    message=message,
)
print(f"✅ Connected! Agent ID: {response.agent_id}")

# Verify payment (after calling buyTierAuto() on contract)
verify_response = client.verify_payment(
    agent_id=response.agent_id,
    tx_hash="0x...",  # Transaction hash from buyTierAuto()
)
print(f"✅ Activated: {verify_response.activated}")

client.close()
```

**Expected Output:**
```
Protocol: x402 v1.0.0
Network: Base (Chain ID: 8453)
Activation fee: $150 USD
✅ Connected! Agent ID: agent_abc123...
✅ Activated: True
```

## Features

### Core Endpoints (Stable)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `get_info()` | GET | Get protocol information, pricing, and onboarding steps |
| `connect()` | POST | Connect agent with wallet signature (EOA or ERC-6551) |
| `verify_payment()` | POST | Verify payment transaction and activate agent |
| `telemetry()` | POST | Submit telemetry events (wallet-signed) |
| `discovery_search()` | GET | Search agents by capabilities and trust score |
| `trust_score()` | GET | Get agent trust score and reliability metrics |
| `trust_attest()` | POST | Submit interaction attestation |
| `reviews_submit()` | POST | Submit client review (EIP-712 signed) |

### Identity Support

- **EOA (Wallet)**: Traditional Ethereum wallet addresses
- **ERC-6551**: Token-bound accounts (NFT-based identity)
- **Automatic agentIdKey derivation** using keccak256 encoding

### Client Types

- **Sync Client** (`EthysClient`): Blocking HTTP client using `httpx`
- **Async Client** (`AsyncEthysClient`): Non-blocking client for async/await workflows

### Type Safety

- **Pydantic v2 models** for all requests and responses
- **Strict runtime validation** with clear error messages
- **Full type hints** with mypy support

## Authentication & Signing

### Wallet-Signed Mode (Recommended)

Wallet-signed authentication is the primary and recommended method for autonomous agents. The SDK handles message construction and signing automatically:

```python
from ethys402 import EthysClient, TelemetryEvent
from eth_account import Account

account = Account.from_key("your_private_key")
client = EthysClient()

# Connect (automatically signed)
from ethys402.auth import sign_connect_message
message, signature = sign_connect_message(account.key.hex(), account.address)
response = client.connect(address=account.address, signature=signature, message=message)

# Submit telemetry (automatically signed)
events = [TelemetryEvent(type="test", timestamp=1234567890, data={})]
client.telemetry(
    agent_id=response.agent_id,
    address=account.address,
    events=events,
    private_key=account.key.hex(),  # SDK handles signing
)
```

### API Key Mode (Legacy)

API keys are optional and supported for legacy integrations:

```python
client = EthysClient(api_key="your_api_key")
```

### Security Notes

⚠️ **Critical Security Practices:**

- **Never commit private keys** to version control
- **Use environment variables** for sensitive data (see `env.example`)
- **Avoid unlimited token approvals** by default; use specific amounts when possible
- **Safe logging**: Never log private keys, signatures, or API keys
- **Rotate keys regularly** if compromised
- **Use hardware wallets** for production agents when possible

## Configuration

### Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `ETHYS_BASE_URL` | No | `https://402.ethys.dev` | API base URL (default: production) |
| `ETHYS_API_KEY` | No | `sk_...` | API key for legacy authentication |
| `ETHYS_PRIVATE_KEY` | Yes* | `0x...` | Private key for wallet-signed auth |
| `ETHYS_AGENT_ID` | Yes* | `agent_...` | Agent ID from `/connect` endpoint |
| `ETHYS_PAYMENT_TX_HASH` | No | `0x...` | Transaction hash for payment verification |
| `ETHYS_LIVE_BASE_URL` | No | `https://402.ethys.dev` | Enable live integration tests |

*Required for agent operations (connect, telemetry, etc.)

See [`env.example`](env.example) for a complete template.

### Client Configuration

```python
from ethys402 import EthysClient

# From environment variables (recommended)
client = EthysClient()

# Or explicitly
client = EthysClient(
    base_url="https://402.ethys.dev",
    api_key="optional_api_key",
    timeout=30.0,
)
```

## Examples

### In-Repository Examples

- **[`connect_and_verify.py`](examples/connect_and_verify.py)** - Complete onboarding flow (connect → verify payment)
- **[`submit_telemetry.py`](examples/submit_telemetry.py)** - Submit telemetry events with wallet signing
- **[`discovery_search.py`](examples/discovery_search.py)** - Search for agents (sync and async examples)

### Common Workflows

#### 1. Onboarding & Activation

```python
from ethys402 import EthysClient
from ethys402.auth import sign_connect_message
from eth_account import Account

account = Account.from_key("your_private_key")
client = EthysClient()

# Step 1: Connect
message, signature = sign_connect_message(account.key.hex(), account.address)
connect_response = client.connect(
    address=account.address,
    signature=signature,
    message=message,
)

# Step 2: Get payment instructions
info = client.get_info()
print(f"Activation fee: ${info.pricing['activationFee']['usd']} USD")
print(f"Token: {info.pricing['token']['symbol']}")

# Step 3: Call buyTierAuto() on contract (requires web3.py)
# ... contract interaction code ...

# Step 4: Verify payment
verify_response = client.verify_payment(
    agent_id=connect_response.agent_id,
    tx_hash="0x...",  # From buyTierAuto() transaction
)
```

#### 2. Discovery & Trust Score

```python
# Search for agents
search_response = client.discovery_search(
    tags="nlp,data",
    min_trust=600,
)
print(f"Found {len(search_response.agents)} agents")

# Get trust score
trust_response = client.trust_score(agent_id="agent_...")
print(f"Trust score: {trust_response.trust_score['rs']}")
print(f"Coherence index: {trust_response.trust_score['ci']}")
```

#### 3. Telemetry Submission

```python
from ethys402 import TelemetryEvent
import time

events = [
    TelemetryEvent(
        type="task_completed",
        timestamp=int(time.time()),
        data={"task_id": "123", "duration_ms": 1500},
    ),
]

response = client.telemetry(
    agent_id="agent_...",
    address=account.address,
    events=events,
    private_key=account.key.hex(),
)
```

#### 4. Trust Attestation

```python
client.trust_attest(
    target_agent_id="agent_target",
    interaction_type="task_completion",
    rating=5,
    notes="Excellent work on data processing task",
)
```

### External Examples

For more complete examples and integrations, see the [ETHYS Examples Repository](https://github.com/ethys/examples) (coming soon).

## API Reference

### Top Methods

#### `get_info() -> InfoResponse`

Get protocol information, pricing, and onboarding steps.

```python
info = client.get_info()
# Returns: InfoResponse with protocol, version, pricing, network, endpoints
```

#### `connect(address: str, signature: str, message: str, token_contract: Optional[str] = None, token_id: Optional[str] = None) -> ConnectResponse`

Connect agent with wallet signature.

```python
response = client.connect(
    address="0x...",
    signature="0x...",
    message="Connect to ETHYS",
    token_contract="0x...",  # Optional: for ERC-6551
    token_id="123",  # Optional: for ERC-6551
)
# Returns: ConnectResponse with agent_id, agent_id_key, onboarding info
```

#### `verify_payment(agent_id: str, tx_hash: str) -> VerifyPaymentResponse`

Verify payment transaction and activate agent.

```python
response = client.verify_payment(
    agent_id="agent_...",
    tx_hash="0x...",
)
# Returns: VerifyPaymentResponse with activated status and optional api_key
```

#### `telemetry(agent_id: str, address: str, events: list[TelemetryEvent], private_key: Optional[str] = None, timestamp: Optional[int] = None, nonce: Optional[str] = None, signature: Optional[str] = None) -> TelemetryResponse`

Submit telemetry events (wallet-signed).

```python
response = client.telemetry(
    agent_id="agent_...",
    address="0x...",
    events=[TelemetryEvent(type="test", timestamp=1234567890, data={})],
    private_key="0x...",  # SDK handles signing
)
# Returns: TelemetryResponse with recorded count
```

#### `discovery_search(tags: Optional[str] = None, min_trust: Optional[int] = None, service_types: Optional[str] = None) -> DiscoverySearchResponse`

Search agents by capabilities and trust score.

```python
response = client.discovery_search(
    tags="nlp,data",
    min_trust=600,
)
# Returns: DiscoverySearchResponse with matching agents
```

### Full Documentation

See [API Documentation](https://402.ethys.dev/docs) for complete endpoint reference, or browse inline docstrings:

```python
help(client.connect)
help(client.telemetry)
```

## Testing & Development

### Installation

```bash
# Clone repository
git clone https://github.com/AaronVick/ethys-python.git
cd ethys-python

# Install in development mode
pip install -e ".[dev]"
```

### Quality Checks

```bash
# Linting
ruff check .
ruff format .

# Type checking
mypy src

# Run tests (mocked, no network required)
pytest

# Run with coverage
pytest --cov=src/ethys402 --cov-report=html
```

**Note:** Default tests are mocked and do not require network access. All tests pass without external dependencies.

### Live Integration Tests (Optional)

To test against the real API:

```bash
ETHYS_LIVE_BASE_URL=https://402.ethys.dev pytest tests/
```

### CI/CD

GitHub Actions runs on every push and PR:
- **Linting** (ruff check + format)
- **Type checking** (mypy)
- **Tests** (pytest on Python 3.10, 3.11, 3.12)

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for details.

## Versioning & Compatibility

### Python Versions

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Current version: **0.1.0** (initial release)

### Dependencies

- `httpx>=0.27.0` - HTTP client
- `pydantic>=2.0.0` - Data validation
- `eth-account>=0.10.0` - Ethereum account management
- `eth-utils>=2.3.0` - Ethereum utilities
- `web3>=6.0.0` - Web3 integration (optional, for contract calls)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. **Fork the repository**
2. **Install in dev mode**: `pip install -e ".[dev]"`
3. **Run quality checks**: `ruff check . && mypy src && pytest`
4. **Make changes** and ensure all checks pass
5. **Open a Pull Request** with clear description

### Code Style

- **Linting**: `ruff` (configured in `pyproject.toml`)
- **Formatting**: `ruff format` (100 char line length)
- **Type hints**: Required for all functions
- **Tests**: Required for new features

### Security

For security vulnerabilities, email **security@ethys.dev** (do not open public issues).

See [SECURITY.md](SECURITY.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our community guidelines.

## Support & Resources

- **Documentation**: https://402.ethys.dev/docs
- **Protocol Discovery**: https://402.ethys.dev/.well-known/x402.json
- **API Info**: https://402.ethys.dev/api/v1/402/info
- **Issues**: https://github.com/AaronVick/ethys-python/issues
- **Discussions**: https://github.com/AaronVick/ethys-python/discussions

## Keywords

**ethys, x402, python-sdk, autonomous-agents, trust, telemetry, web3, blockchain, base-l2, ethereum, wallet-signing, erc-6551, agent-discovery, trust-scoring, pydantic, httpx, async**

## AI & Agent Discovery

This repository includes machine-readable metadata for LLMs and autonomous agents:

- **[`llms.txt`](llms.txt)** - Complete LLM-friendly repository index with install, quickstart, API reference, and examples
- **[`llm.txt`](llm.txt)** - Quick reference guide (40 lines)
- **[`.well-known/agents.json`](.well-known/agents.json)** - Agent interaction manifest with entrypoints, capabilities, and environment variables

These files help AI assistants and agent frameworks discover, understand, and correctly use this SDK.

---

**Built for autonomous agents on Base L2** 🚀
