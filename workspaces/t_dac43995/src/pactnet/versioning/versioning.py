"""Contract versioning and compatibility reporting."""
import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class CompatibilityLevel(Enum):
    """Compatibility levels between contract versions."""
    COMPATIBLE = "compatible"
    BACKWARDS_INCOMPATIBLE = "backwards_incompatible"
    UNKNOWN = "unknown"


@dataclass
class BreakingChange:
    """A breaking change between contract versions."""
    type: str
    description: str
    interaction: str = ""
    field: str = ""

    def __str__(self) -> str:
        prefix = f"[{self.interaction}]" if self.interaction else ""
        suffix = f".{self.field}" if self.field else ""
        return f"{prefix}{suffix}: {self.description}"


@dataclass
class CompatibilityReport:
    """Report comparing two contract versions."""
    consumer_name: str
    provider_name: str
    old_version: str
    new_version: str
    changes: list[BreakingChange] = field(default_factory=list)

    @property
    def level(self) -> CompatibilityLevel:
        if any(c.type == "breaking" for c in self.changes):
            return CompatibilityLevel.BACKWARDS_INCOMPATIBLE
        if self.changes:
            return CompatibilityLevel.COMPATIBLE
        return CompatibilityLevel.UNKNOWN

    @property
    def breaking_changes(self) -> list[BreakingChange]:
        return [c for c in self.changes if c.type == "breaking"]

    @property
    def non_breaking_changes(self) -> list[BreakingChange]:
        return [c for c in self.changes if c.type != "breaking"]

    def to_dict(self) -> dict:
        return {
            "consumer": self.consumer_name,
            "provider": self.provider_name,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "compatibility": self.level.value,
            "breaking_changes": [str(c) for c in self.breaking_changes],
            "non_breaking_changes": [str(c) for c in self.non_breaking_changes],
        }

    def __str__(self) -> str:
        status = self.level.value.upper()
        return (
            f"[{status}] {self.old_version} -> {self.new_version}: "
            f"{len(self.breaking_changes)} breaking, "
            f"{len(self.non_breaking_changes)} non-breaking changes"
        )


class ContractVersioner:
    """Track contract versions and detect breaking changes."""

    def __init__(self, version_dir: Path):
        self.version_dir = Path(version_dir)
        self.version_dir.mkdir(parents=True, exist_ok=True)

    def save_version(
        self,
        contract: dict,
        version: str,
    ) -> Path:
        """Save a contract version."""
        version_file = self.version_dir / f"v{version}.json"
        version_file.write_text(
            json.dumps(contract, indent=2, default=str),
            encoding="utf-8",
        )
        return version_file

    def load_version(self, version: str) -> dict:
        """Load a specific contract version."""
        version_file = self.version_dir / f"v{version}.json"
        if not version_file.exists():
            raise FileNotFoundError(f"Version {version} not found at {version_file}")
        return json.loads(version_file.read_text(encoding="utf-8"))

    def list_versions(self) -> list[str]:
        """List all saved versions."""
        versions = []
        for f in sorted(self.version_dir.glob("v*.json")):
            versions.append(f.stem[1:])  # strip 'v' prefix
        return versions

    def compare(
        self,
        old_version: str,
        new_version: str,
    ) -> CompatibilityReport:
        """Compare two contract versions and detect breaking changes."""
        old = self.load_version(old_version)
        new = self.load_version(new_version)

        report = CompatibilityReport(
            consumer_name=new.get("consumer", {}).get("name", "unknown"),
            provider_name=new.get("provider", {}).get("name", "unknown"),
            old_version=old_version,
            new_version=new_version,
        )

        old_interactions = {
            self._interaction_key(i): i
            for i in old.get("interactions", [])
        }
        new_interactions = {
            self._interaction_key(i): i
            for i in new.get("interactions", [])
        }

        # Removed interactions = breaking
        for key, interaction in old_interactions.items():
            if key not in new_interactions:
                report.changes.append(BreakingChange(
                    type="breaking",
                    description=f"Interaction removed: {interaction.get('description', key)}",
                    interaction=interaction.get("description", ""),
                ))

        # Added interactions = non-breaking
        for key, interaction in new_interactions.items():
            if key not in old_interactions:
                report.changes.append(BreakingChange(
                    type="additive",
                    description=f"New interaction added: {interaction.get('description', key)}",
                    interaction=interaction.get("description", ""),
                ))

        # Changed interactions
        for key in old_interactions:
            if key in new_interactions:
                old_i = old_interactions[key]
                new_i = new_interactions[key]
                self._compare_interaction(old_i, new_i, report)

        return report

    def _interaction_key(self, interaction: dict) -> str:
        """Create a unique key for an interaction based on its description."""
        return interaction.get("description", "")

    def _compare_interaction(
        self,
        old: dict,
        new: dict,
        report: CompatibilityReport,
    ) -> None:
        """Compare two versions of the same interaction."""
        old_req = old.get("request", {})
        new_req = new.get("request", {})

        if old_req.get("path") != new_req.get("path"):
            report.changes.append(BreakingChange(
                type="breaking",
                description=f"Request path changed from '{old_req.get('path')}' to '{new_req.get('path')}'",
                interaction=old.get("description", ""),
                field="request.path",
            ))

        if old_req.get("method") != new_req.get("method"):
            report.changes.append(BreakingChange(
                type="breaking",
                description=f"Request method changed from '{old_req.get('method')}' to '{new_req.get('method')}'",
                interaction=old.get("description", ""),
                field="request.method",
            ))

        old_body = old_req.get("body", {})
        new_body = new_req.get("body", {})
        self._compare_body(old_body, new_body, "request", old.get("description", ""), report)

        old_resp = old.get("response", {})
        new_resp = new.get("response", {})

        if old_resp.get("status") != new_resp.get("status"):
            report.changes.append(BreakingChange(
                type="breaking",
                description=f"Response status changed from {old_resp.get('status')} to {new_resp.get('status')}",
                interaction=old.get("description", ""),
                field="response.status",
            ))

        old_resp_body = old_resp.get("body", {})
        new_resp_body = new_resp.get("body", {})
        self._compare_body(old_resp_body, new_resp_body, "response", old.get("description", ""), report)

    def _compare_body(
        self,
        old_body: Any,
        new_body: Any,
        context: str,
        interaction_desc: str,
        report: CompatibilityReport,
    ) -> None:
        """Recursively compare request/response body schemas."""
        if isinstance(old_body, dict) and isinstance(new_body, dict):
            for key in old_body:
                if key not in new_body:
                    report.changes.append(BreakingChange(
                        type="breaking",
                        description=f"Field '{key}' removed from {context} body",
                        interaction=interaction_desc,
                        field=f"{context}.body.{key}",
                    ))
                else:
                    self._compare_body(
                        old_body[key], new_body[key],
                        context, interaction_desc, report,
                    )
            for key in new_body:
                if key not in old_body:
                    report.changes.append(BreakingChange(
                        type="additive",
                        description=f"New field '{key}' added to {context} body",
                        interaction=interaction_desc,
                        field=f"{context}.body.{key}",
                    ))
        elif type(old_body) != type(new_body):
            report.changes.append(BreakingChange(
                type="breaking",
                description=f"Type of {context} body changed from {type(old_body).__name__} to {type(new_body).__name__}",
                interaction=interaction_desc,
                field=f"{context}.body",
            ))


def compare_contracts(
    old_path: Path,
    new_path: Path,
) -> CompatibilityReport:
    """Convenience: compare two contract files and return a compatibility report."""
    old = json.loads(Path(old_path).read_text(encoding="utf-8"))
    new = json.loads(Path(new_path).read_text(encoding="utf-8"))

    # Create a temporary versioner to use its compare logic
    versioner = ContractVersioner(version_dir=Path("/tmp/pactnet_compare"))

    # Manually construct the report since we're comparing files, not saved versions
    report = CompatibilityReport(
        consumer_name=new.get("consumer", {}).get("name", "unknown"),
        provider_name=new.get("provider", {}).get("name", "unknown"),
        old_version=str(old_path),
        new_version=str(new_path),
    )

    old_interactions = {
        versioner._interaction_key(i): i for i in old.get("interactions", [])
    }
    new_interactions = {
        versioner._interaction_key(i): i for i in new.get("interactions", [])
    }

    for key, interaction in old_interactions.items():
        if key not in new_interactions:
            report.changes.append(BreakingChange(
                type="breaking",
                description=f"Interaction removed: {interaction.get('description', key)}",
                interaction=interaction.get("description", ""),
            ))

    for key, interaction in new_interactions.items():
        if key not in old_interactions:
            report.changes.append(BreakingChange(
                type="additive",
                description=f"New interaction added: {interaction.get('description', key)}",
                interaction=interaction.get("description", ""),
            ))

    for key in old_interactions:
        if key in new_interactions:
            versioner._compare_interaction(old_interactions[key], new_interactions[key], report)

    return report
