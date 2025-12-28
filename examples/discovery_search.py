"""Example: Search for agents using discovery."""

from ethys402 import AsyncEthysClient, EthysClient


def main_sync():
    """Synchronous discovery search example."""
    client = EthysClient()

    try:
        print("🔍 Searching for agents...")
        print("   Tags: nlp, data")
        print("   Min trust score: 600")

        response = client.discovery_search(
            tags="nlp,data",
            min_trust=600,
        )

        if response.success:
            print(f"\n✅ Found {len(response.agents)} agents")
            if response.total is not None:
                print(f"   Total: {response.total}")

            for agent in response.agents[:5]:  # Show first 5
                agent_id = agent.get("agentId", "unknown")
                tags = agent.get("tags", [])
                min_trust = agent.get("minTrust", 0)
                print(f"\n   Agent: {agent_id}")
                print(f"   Tags: {', '.join(tags)}")
                print(f"   Min Trust: {min_trust}")
        else:
            print("❌ Search failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    finally:
        client.close()


async def main_async():
    """Asynchronous discovery search example."""
    async with AsyncEthysClient() as client:
        print("🔍 Searching for agents (async)...")
        print("   Tags: nlp")
        print("   Min trust score: 500")

        response = await client.discovery_search(
            tags="nlp",
            min_trust=500,
        )

        if response.success:
            print(f"\n✅ Found {len(response.agents)} agents")
            for agent in response.agents[:3]:
                print(f"   - {agent.get('agentId', 'unknown')}")


if __name__ == "__main__":
    import asyncio

    print("=== Synchronous Example ===")
    main_sync()

    print("\n=== Asynchronous Example ===")
    asyncio.run(main_async())

