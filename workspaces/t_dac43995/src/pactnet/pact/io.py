"""Pact file reader/writer - serialization and deserialization."""
import json
from pathlib import Path
from typing import Optional


class PactWriter:
    """Writes contract to JSON file in Pact specification format."""

    def __init__(self, contract):
        self.contract = contract

    def write(self, output_path: Path) -> Path:
        """Write contract to JSON file."""
        data = self.contract.to_dict()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
        return output_path


class PactReader:
    """Reads a Pact contract from JSON file."""

    def __init__(self, path: Optional[Path] = None):
        self.path = path
        self.data: dict = {}

    def read(self, path: Path):
        """Read contract from JSON file."""
        # Deferred import to avoid circular dependency
        from pactnet.consumer.interaction import Contract, Interaction

        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

        contract = Contract(
            consumer_name=self.data["consumer"]["name"],
            provider_name=self.data["provider"]["name"],
        )

        for interaction_data in self.data.get("interactions", []):
            interaction = Interaction(
                description=interaction_data.get("description", ""),
                provider_state=interaction_data.get("providerState"),
                request=interaction_data.get("request"),
                response=interaction_data.get("response"),
            )
            contract.add_interaction(interaction)

        return contract


def write_pact(contract, output_path: Path) -> Path:
    """Convenience: write contract to file."""
    return PactWriter(contract).write(output_path)


def read_pact(path: Path):
    """Convenience: read contract from file."""
    return PactReader().read(path)
