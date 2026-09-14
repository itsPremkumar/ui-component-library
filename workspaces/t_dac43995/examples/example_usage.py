"""Example: Using PactNet to define and verify a contract."""
import json
from pathlib import Path
from pactnet.consumer import consumer
from pactnet.pact import write_pact
from pactnet.provider import verify_provider
from pactnet.mock_server import MockServer


def main():
    # Step 1: Consumer defines what it expects from the provider
    print("=" * 60)
    print("Step 1: Consumer defines the contract")
    print("=" * 60)

    contract = consumer("order-service")
    contract.provider_name = "payment-service"

    # Define interaction: create payment
    interaction = contract.new_interaction("create payment")
    interaction.given("valid payment request")
    interaction.with_request(
        "POST", "/api/payments",
        body={"order_id": "ord-123", "amount": 99.99, "currency": "USD"},
    )
    interaction.will_respond_with(
        201,
        body={"payment_id": "pay-456", "status": "authorized"},
    )

    # Define interaction: get payment status
    interaction2 = contract.new_interaction("get payment status")
    interaction2.given("payment pay-456 exists")
    interaction2.with_request("GET", "/api/payments/pay-456")
    interaction2.will_respond_with(
        200,
        body={"payment_id": "pay-456", "status": "authorized", "amount": 99.99},
    )

    print(f"Contract: {contract}")
    print(f"Interactions: {len(contract)}")

    # Step 2: Write the contract to a file
    print("\n" + "=" * 60)
    print("Step 2: Write contract to Pact file")
    print("=" * 60)

    pact_path = Path("payment-pact.json")
    write_pact(contract, pact_path)
    print(f"Written to: {pact_path.absolute()}")

    # Step 3: Start mock server for consumer development
    print("\n" + "=" * 60)
    print("Step 3: Start mock server for consumer development")
    print("=" * 60)

    server = MockServer(host="localhost", port=8080)
    count = server.load_pact(pact_path)
    server.start()
    print(f"Mock server running at {server.url} ({count} interactions loaded)")

    # Step 4: Verify the mock (or real) provider against the contract
    print("\n" + "=" * 60)
    print("Step 4: Verify provider against contract")
    print("=" * 60)

    report = verify_provider("http://localhost:8080", pact_path)
    print(report)

    for result in report.results:
        status = "OK" if result.success else "FAIL"
        print(f"  [{status}] {result.interaction_description}")
        if result.error:
            print(f"        Error: {result.error}")

    server.stop()

    # Step 5: Show contract versioning
    print("\n" + "=" * 60)
    print("Step 5: Contract compatibility check")
    print("=" * 60)

    from pactnet.versioning import ContractVersioner

    versioner = ContractVersioner(Path("pact-versions"))
    versioner.save_version(contract.to_dict(), "1.0.0")

    # Simulate a v2 with an added field
    v2_dict = contract.to_dict()
    v2_dict["interactions"][0]["response"]["body"]["transaction_id"] = "txn-789"
    versioner.save_version(v2_dict, "1.1.0")

    compat = versioner.compare("1.0.0", "1.1.0")
    print(compat)
    for change in compat.changes:
        print(f"  - {change}")


if __name__ == "__main__":
    main()
