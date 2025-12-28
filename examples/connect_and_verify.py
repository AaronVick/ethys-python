"""Example: Connect agent and verify payment."""

import os
from eth_account import Account

from ethys402 import EthysClient
from ethys402.auth import sign_connect_message


def main():
    """Connect agent and verify payment example."""
    # Get private key from environment or use a test key
    private_key = os.environ.get("ETHYS_PRIVATE_KEY")
    if not private_key:
        print("Creating a test account (for demo only)")
        account = Account.create()
        private_key = account.key.hex()
        print(f"Test address: {account.address}")
        print(f"Test private key: {private_key}")
        print("\n⚠️  This is a test account. Use your real private key in production!")
    else:
        account = Account.from_key(private_key)

    # Initialize client
    client = EthysClient()

    try:
        # Step 1: Get protocol info
        print("\n📋 Fetching protocol info...")
        info = client.get_info()
        print(f"Protocol: {info.protocol} v{info.version}")
        print(f"Network: {info.network.get('name', 'Unknown')} (Chain ID: {info.network.get('chainId')})")
        print(f"Activation fee: ${info.pricing.get('activationFee', {}).get('usd', 'Unknown')} USD")

        # Step 2: Connect with wallet signature
        print("\n🔐 Connecting agent...")
        message, signature = sign_connect_message(
            private_key, account.address, message="Connect to ETHYS"
        )

        connect_response = client.connect(
            address=account.address,
            signature=signature,
            message=message,
        )

        print(f"✅ Connected! Agent ID: {connect_response.agent_id}")
        if connect_response.agent_id_key:
            print(f"   Agent ID Key: {connect_response.agent_id_key}")

        # Step 3: Verify payment (if you have a transaction hash)
        tx_hash = os.environ.get("ETHYS_PAYMENT_TX_HASH")
        if tx_hash:
            print(f"\n💳 Verifying payment (tx: {tx_hash[:10]}...)")
            verify_response = client.verify_payment(
                agent_id=connect_response.agent_id,
                tx_hash=tx_hash,
            )

            if verify_response.activated:
                print("✅ Payment verified! Agent activated.")
                if verify_response.api_key:
                    print(f"   API Key: {verify_response.api_key[:20]}...")
            else:
                print("❌ Payment verification failed")
        else:
            print("\n💡 To verify payment, set ETHYS_PAYMENT_TX_HASH environment variable")
            print("   After calling buyTierAuto() on the purchase contract, use the tx hash here")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()

