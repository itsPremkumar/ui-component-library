"""CLI for PactNet - contract testing framework."""
import json
import sys
from pathlib import Path

from pactnet.consumer.interaction import Contract, Interaction
from pactnet.pact.io import PactWriter, PactReader
from pactnet.provider.verifier import ProviderVerifier, verify_provider
from pactnet.versioning.versioning import ContractVersioner, compare_contracts


def create_contract(args):
    """Create a new contract interactively or from args."""
    contract = Contract(
        consumer_name=args.consumer,
        provider_name=args.provider,
    )

    # Add a sample interaction
    interaction = contract.new_interaction("Sample interaction")
    interaction.with_request("GET", "/api/health")
    interaction.will_respond_with(200, body={"status": "ok"})

    output = Path(args.output)
    PactWriter(contract).write(output)
    print(f"Contract written to {output}")


def verify(args):
    """Verify a provider against a contract file."""
    report = verify_provider(
        provider_base_url=args.provider_url,
        pact_path=Path(args.pact_file),
    )

    print(report)

    if args.output:
        Path(args.output).write_text(
            json.dumps(report.to_dict(), indent=2),
            encoding="utf-8",
        )
        print(f"Report written to {args.output}")

    sys.exit(0 if report.success else 1)


def compare(args):
    """Compare two contract versions."""
    report = compare_contracts(
        old_path=Path(args.old),
        new_path=Path(args.new),
    )

    print(report)
    for change in report.changes:
        print(f"  - {change}")


def version(args):
    """Manage contract versions."""
    versioner = ContractVersioner(Path(args.version_dir))

    if args.action == "save":
        contract = json.loads(Path(args.contract_file).read_text(encoding="utf-8"))
        versioner.save_version(contract, args.version)
        print(f"Version {args.version} saved")
    elif args.action == "list":
        versions = versioner.list_versions()
        for v in versions:
            print(f"  v{v}")
    elif args.action == "compare":
        report = versioner.compare(args.old_version, args.new_version)
        print(report)
        for change in report.changes:
            print(f"  - {change}")


def serve(args):
    """Start a mock server from a Pact file."""
    from pactnet.mock_server.server import MockServer

    server = MockServer(host=args.host, port=args.port)
    count = server.load_pact(Path(args.pact_file))
    server.start()
    print(f"Mock server running at {server.url} ({count} interactions loaded)")
    print("Press Ctrl+C to stop")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("\nServer stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="pactnet",
        description="PactNet - Consumer-Driven Contract Testing Framework",
    )
    subparsers = parser.add_subparsers(dest="command")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new contract")
    create_parser.add_argument("--consumer", required=True, help="Consumer name")
    create_parser.add_argument("--provider", required=True, help="Provider name")
    create_parser.add_argument("--output", required=True, help="Output Pact file path")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Verify a provider against a contract")
    verify_parser.add_argument("--pact-file", required=True, help="Path to Pact file")
    verify_parser.add_argument("--provider-url", required=True, help="Provider base URL")
    verify_parser.add_argument("--output", help="Output report file path")

    # compare
    compare_parser = subparsers.add_parser("compare", help="Compare two contract versions")
    compare_parser.add_argument("--old", required=True, help="Old contract file path")
    compare_parser.add_argument("--new", required=True, help="New contract file path")

    # version
    version_parser = subparsers.add_parser("version", help="Manage contract versions")
    version_parser.add_argument("action", choices=["save", "list", "compare"])
    version_parser.add_argument("--version-dir", default="./pact-versions", help="Version directory")
    version_parser.add_argument("--contract-file", help="Contract file to save")
    version_parser.add_argument("--version", help="Version tag")
    version_parser.add_argument("--old-version", help="Old version to compare")
    version_parser.add_argument("--new-version", help="New version to compare")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start mock server from Pact file")
    serve_parser.add_argument("--pact-file", required=True, help="Path to Pact file")
    serve_parser.add_argument("--host", default="localhost", help="Server host")
    serve_parser.add_argument("--port", type=int, default=8080, help="Server port")

    args = parser.parse_args()

    if args.command == "create":
        create_contract(args)
    elif args.command == "verify":
        verify(args)
    elif args.command == "compare":
        compare(args)
    elif args.command == "version":
        version(args)
    elif args.command == "serve":
        serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
