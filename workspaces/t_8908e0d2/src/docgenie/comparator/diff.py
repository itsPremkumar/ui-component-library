"""API specification version comparator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChangeType(str, Enum):
    """Types of changes between API versions."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"


@dataclass
class Change:
    """A single change between API versions."""
    change_type: ChangeType
    category: str  # endpoint, parameter, schema, response
    path: str
    detail: str = ""
    old_value: Any = None
    new_value: Any = None


@dataclass
class ComparisonResult:
    """Result of comparing two API specs."""
    spec_a_title: str = ""
    spec_a_version: str = ""
    spec_b_title: str = ""
    spec_b_version: str = ""
    changes: list[Change] = field(default_factory=list)

    @property
    def breaking_changes(self) -> list[Change]:
        """Return breaking changes (removals, type changes)."""
        return [c for c in self.changes if c.change_type in (ChangeType.REMOVED,) or
                (c.change_type == ChangeType.MODIFIED and c.category in ("endpoint", "schema"))]

    @property
    def additions(self) -> list[Change]:
        """Return added items."""
        return [c for c in self.changes if c.change_type == ChangeType.ADDED]

    @property
    def is_compatible(self) -> bool:
        """Check if the change is backward compatible."""
        return len(self.breaking_changes) == 0

    def summary(self) -> str:
        """Return a human-readable summary."""
        lines = [
            f"Comparing {self.spec_a_title} {self.spec_a_version} → {self.spec_b_title} {self.spec_b_version}",
            f"Total changes: {len(self.changes)}",
            f"  Added: {len([c for c in self.changes if c.change_type == ChangeType.ADDED])}",
            f"  Removed: {len([c for c in self.changes if c.change_type == ChangeType.REMOVED])}",
            f"  Modified: {len([c for c in self.changes if c.change_type == ChangeType.MODIFIED])}",
            f"  Deprecated: {len([c for c in self.changes if c.change_type == ChangeType.DEPRECATED])}",
            f"Breaking changes: {len(self.breaking_changes)}",
            f"Backward compatible: {'Yes' if self.is_compatible else 'No'}",
        ]
        return "\n".join(lines)


class SpecComparator:
    """Compare two OpenAPI specifications."""

    def __init__(self) -> None:
        pass

    def compare(self, spec_a: Any, spec_b: Any) -> ComparisonResult:
        """Compare two parsed OpenAPI specs."""
        result = ComparisonResult(
            spec_a_title=spec_a.title,
            spec_a_version=spec_a.version,
            spec_b_title=spec_b.title,
            spec_b_version=spec_b.version,
        )

        self._compare_endpoints(spec_a, spec_b, result)
        self._compare_schemas(spec_a, spec_b, result)

        return result

    def _compare_endpoints(self, spec_a: Any, spec_b: Any, result: ComparisonResult) -> None:
        """Compare endpoints between two specs."""
        endpoints_a = {(e.method, e.path): e for e in spec_a.endpoints}
        endpoints_b = {(e.method, e.path): e for e in spec_b.endpoints}

        # Removed endpoints
        for key, ep in endpoints_a.items():
            if key not in endpoints_b:
                result.changes.append(Change(
                    change_type=ChangeType.REMOVED,
                    category="endpoint",
                    path=f"{ep.method} {ep.path}",
                    detail="Endpoint removed",
                    old_value=ep.summary,
                ))

        # Added endpoints
        for key, ep in endpoints_b.items():
            if key not in endpoints_a:
                result.changes.append(Change(
                    change_type=ChangeType.ADDED,
                    category="endpoint",
                    path=f"{ep.method} {ep.path}",
                    detail="Endpoint added",
                    new_value=ep.summary,
                ))

        # Modified endpoints
        for key in set(endpoints_a.keys()) & set(endpoints_b.keys()):
            ep_a = endpoints_a[key]
            ep_b = endpoints_b[key]

            if ep_a.summary != ep_b.summary:
                result.changes.append(Change(
                    change_type=ChangeType.MODIFIED,
                    category="endpoint",
                    path=f"{ep_a.method} {ep_a.path}",
                    detail="Summary changed",
                    old_value=ep_a.summary,
                    new_value=ep_b.summary,
                ))

            if ep_a.description != ep_b.description:
                result.changes.append(Change(
                    change_type=ChangeType.MODIFIED,
                    category="endpoint",
                    path=f"{ep_a.method} {ep_a.path}",
                    detail="Description changed",
                    old_value=ep_a.description,
                    new_value=ep_b.description,
                ))

            # Check for deprecation
            if not ep_a.deprecated and ep_b.deprecated:
                result.changes.append(Change(
                    change_type=ChangeType.DEPRECATED,
                    category="endpoint",
                    path=f"{ep_a.method} {ep_a.path}",
                    detail="Endpoint deprecated",
                ))

            # Compare parameters
            self._compare_parameters(ep_a, ep_b, result)

    def _compare_parameters(self, ep_a: Any, ep_b: Any, result: ComparisonResult) -> None:
        """Compare parameters of two endpoints."""
        params_a = {p.get("name", ""): p for p in ep_a.parameters}
        params_b = {p.get("name", ""): p for p in ep_b.parameters}

        for name, param in params_a.items():
            if name not in params_b:
                result.changes.append(Change(
                    change_type=ChangeType.REMOVED,
                    category="parameter",
                    path=f"{ep_a.method} {ep_a.path} — {name}",
                    detail=f"Parameter '{name}' removed",
                ))

        for name, param in params_b.items():
            if name not in params_a:
                result.changes.append(Change(
                    change_type=ChangeType.ADDED,
                    category="parameter",
                    path=f"{ep_b.method} {ep_b.path} — {name}",
                    detail=f"Parameter '{name}' added",
                ))

    def _compare_schemas(self, spec_a: Any, spec_b: Any, result: ComparisonResult) -> None:
        """Compare schema definitions between two specs."""
        schemas_a = set(spec_a.schemas.keys())
        schemas_b = set(spec_b.schemas.keys())

        for name in schemas_a - schemas_b:
            result.changes.append(Change(
                change_type=ChangeType.REMOVED,
                category="schema",
                path=name,
                detail=f"Schema '{name}' removed",
            ))

        for name in schemas_b - schemas_a:
            result.changes.append(Change(
                change_type=ChangeType.ADDED,
                category="schema",
                path=name,
                detail=f"Schema '{name}' added",
            ))

        for name in schemas_a & schemas_b:
            schema_a = spec_a.schemas[name]
            schema_b = spec_b.schemas[name]
            if schema_a != schema_b:
                result.changes.append(Change(
                    change_type=ChangeType.MODIFIED,
                    category="schema",
                    path=name,
                    detail=f"Schema '{name}' modified",
                ))
