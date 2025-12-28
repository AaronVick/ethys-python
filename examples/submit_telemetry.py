"""Example: Submit telemetry events."""

import os
import time
from eth_account import Account

from ethys402 import EthysClient, TelemetryEvent


def main():
    """Submit telemetry example."""
    # Get credentials
    private_key = os.environ.get("ETHYS_PRIVATE_KEY")
    if not private_key:
        raise ValueError("ETHYS_PRIVATE_KEY environment variable required")

    agent_id = os.environ.get("ETHYS_AGENT_ID")
    if not agent_id:
        raise ValueError("ETHYS_AGENT_ID environment variable required")

    account = Account.from_key(private_key)

    # Initialize client
    client = EthysClient()

    try:
        # Create telemetry events
        events = [
            TelemetryEvent(
                type="agent_start",
                timestamp=int(time.time()),
                data={
                    "version": "1.0.0",
                    "capabilities": ["nlp", "data_processing"],
                },
            ),
            TelemetryEvent(
                type="task_completed",
                timestamp=int(time.time()),
                data={
                    "task_id": "task_123",
                    "duration_ms": 1500,
                    "success": True,
                },
            ),
        ]

        print(f"📊 Submitting {len(events)} telemetry events...")
        print(f"   Agent ID: {agent_id}")
        print(f"   Address: {account.address}")

        # Submit telemetry (wallet-signed)
        response = client.telemetry(
            agent_id=agent_id,
            address=account.address,
            events=events,
            private_key=private_key,
        )

        if response.success:
            print(f"✅ Telemetry recorded! ({response.recorded} events)")
        else:
            print("❌ Failed to record telemetry")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()

