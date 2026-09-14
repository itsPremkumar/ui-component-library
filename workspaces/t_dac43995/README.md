# PactNet — Consumer-Driven Contract Testing Framework

A Python framework for implementing consumer-driven contract (CDC) testing for service-to-service APIs. Inspired by [Pact](https://pact.io/), PactNet enables teams to catch integration issues early by defining clear contracts between consumers and providers.

## Features

- **Consumer-Driven Contracts** — Consumers define expected interactions; providers verify against them
- **Fluent API** — Builder pattern for readable contract definitions
- **Mock Server** — Standalone HTTP mock for consumer development (no real provider needed)
- **Provider Verification** — Automated verification of live/provider APIs against contracts
- **Contract Versioning** — Track contract evolution and detect breaking changes
- **CLI Tool** — Full command-line interface for CI/CD integration
- **Pact Specification v3** — Compatible with the Pact contract format

## Quickstart

### Install

```bash
pip install -e ".[dev]"
```

### Define a Contract (Consumer Side)

```python
from pactnet.consumer import consumer
from pactnet.pact import write_pact
from pathlib import Path

# Create a contract as the consumer
contract = consumer("order-service")
contract.provider_name = "payment-service"

# Define expected interactions
interaction = contract.new_interaction("create payment")
interaction.given("valid payment request")
interaction.with_request(
    "POST", "/api/payments",
    body={"order_id": "ord-123", "amount": 99.99}
)
interaction.will_respond_with(
    201,
    body={"payment_id": "pay-456", "status": "authorized"}
)

# Write to a Pact JSON file
write_pact(contract, Path("pact.json"))
```

### Start Mock Server (for Consumer Development)

```bash
# Via CLI
pactnet serve --pact-file pact.json --port 8080

# Or programmatically
from pactnet.mock_server import MockServer
from pathlib import Path

with MockServer(host="localhost", port=8080) as server:
    server.load_pact(Path("pact.json"))
    # Your consumer code can now hit http://localhost:8080
```

### Verify the Provider

```bash
# CLI
pactnet verify --pact-file pact.json --provider-url http://api.example.com

# Or programmatically
from pactnet.provider import verify_provider

report = verify_provider("http://api.example.com", Path("pact.json"))
print(f"Passed: {report.passed}/{report.total}")
```

## Contract Authoring Guide

### Contract Structure

A contract is defined between a **consumer** and a **provider**. Each contract contains one or more **interactions**.

### Interactions

Each interaction defines:
1. **Description** — What the interaction is about
2. **Provider State** — Precondition on the provider side
3. **Request** — What the consumer sends (method, path, headers, body)
4. **Response** — What the provider returns (status, headers, body)

```python
contract = consumer("my-frontend")
contract.provider_name = "user-api"

interaction = contract.new_interaction("get user by ID")
interaction.given("user with ID 123 exists")  # Provider state
interaction.with_request(
    "GET", "/api/users/123",
    headers={"Accept": "application/json"}
)
interaction.will_respond_with(
    200,
    headers={"Content-Type": "application/json"},
    body={"id": 123, "name": "Alice", "email": "alice@example.com"}
)
```

### Matchers

Matchers allow flexible matching in contracts:

```python
from pactnet.pact.matcher import like, regex, integer, each_like

# Match any value of the same type
body={"id": integer(1), "name": like("Alice")}

# Match by regex
body={"email": regex(r"^[\w.-]+@[\w.-]+\.\w+$", "user@example.com")}

# Match arrays
body={"items": each_like({"id": 1, "name": "item"}, min_count=1)}
```

## Verification Workflow

```
  Consumer                      Provider
     |                             |
     |--- define contract --------->|  (Write Pact JSON)
     |                             |
     |--- develop against mock ---->|  (Mock Server)
     |                             |
     |                             |-- implement API
     |                             |
     |<----- verify contract ------|  (Provider Verification)
```

1. **Consumer** writes the contract (Pact JSON)
2. **Consumer** develops against the **Mock Server**
3. **Provider** implements the real API
4. **Provider** verifies their implementation against the contract

### Setup/Teardown Hooks

```python
from pactnet.provider import ProviderVerifier

verifier = ProviderVerifier("http://provider:8080")
verifier.add_setup_hook(lambda state: seed_database(state))
verifier.add_teardown_hook(lambda state: cleanup_database(state))

report = verifier.verify_pact_file(Path("pact.json"))
```

## CLI Reference

### `pactnet create`
Create a new contract file.
```bash
pactnet create --consumer order-service --provider user-service --output pact.json
```

### `pactnet serve`
Start a mock server from a contract.
```bash
pactnet serve --pact-file pact.json --host localhost --port 8080
```

### `pactnet verify`
Verify a provider against a contract.
```bash
pactnet verify --pact-file pact.json --provider-url http://api.example.com
```

### `pactnet compare`
Compare two contract versions for compatibility.
```bash
pactnet compare --old v1.json --new v2.json
```

### `pactnet version`
Manage contract versions.
```bash
pactnet version save --contract-file pact.json --version 1.0.0
pactnet version list
pactnet version compare --old-version 1.0.0 --new-version 2.0.0
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Contract Tests
on: [push, pull_request]

jobs:
  contract-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: pytest tests/
      - run: pactnet verify --pact-file contracts/*.json --provider-url ${{ secrets.PROVIDER_URL }}
```

### Breaking Change Detection

```bash
# Compare current contract with previous version
pactnet compare --old contracts/v1.json --new contracts/v2.json

# Non-zero exit code on breaking changes
echo $?  # 0 = compatible, 1 = breaking
```

## Contract Versioning

PactNet tracks contract evolution and detects breaking changes:

- **Additive** (safe): New interactions, new optional fields
- **Breaking** (unsafe): Removed interactions, changed paths, changed status codes

```python
from pactnet.versioning import ContractVersioner

versioner = ContractVersioner(Path("./pact-versions"))
versioner.save_version(contract_dict, "1.0.0")
versioner.save_version(contract_dict_v2, "2.0.0")

report = versioner.compare("1.0.0", "2.0.0")
print(report.breaking_changes)  # list of BreakingChange objects
```

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
