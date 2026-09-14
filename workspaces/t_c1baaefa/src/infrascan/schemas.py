"""Shared data schemas for InfraScan."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceType(str, Enum):
    """Supported IaC resource types."""
    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"
    PULUMI = "pulumi"
    GENERIC = "generic"


@dataclass
class Resource:
    """Represents a scanned infrastructure resource."""
    name: str
    resource_type: str  # e.g., "aws_s3_bucket"
    source_file: str
    line_start: int = 0
    line_end: int = 0
    properties: dict[str, Any] = field(default_factory=dict)
    iac_type: ResourceType = ResourceType.GENERIC


@dataclass
class Finding:
    """A single security, compliance, or cost finding."""
    rule_id: str
    title: str
    description: str
    severity: Severity
    resource: Optional[Resource] = None
    file_path: str = ""
    line_number: int = 0
    remediation: str = ""
    references: list[str] = field(default_factory=list)
    category: str = "security"  # security, compliance, cost
    confidence: str = "high"  # high, medium, low

    def to_dict(self) -> dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path or (self.resource.source_file if self.resource else ""),
            "line_number": self.line_number,
            "resource_type": self.resource.resource_type if self.resource else "",
            "resource_name": self.resource.name if self.resource else "",
            "remediation": self.remediation,
            "references": self.references,
            "category": self.category,
            "confidence": self.confidence,
        }


@dataclass
class ScanResult:
    """Aggregated results from a scan."""
    findings: list[Finding] = field(default_factory=list)
    resources_scanned: int = 0
    files_scanned: int = 0
    scan_duration_seconds: float = 0.0
    iac_types: list[ResourceType] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.INFO)

    def by_category(self, category: str) -> list[Finding]:
        return [f for f in self.findings if f.category == category]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "total_findings": len(self.findings),
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
                "resources_scanned": self.resources_scanned,
                "files_scanned": self.files_scanned,
                "scan_duration_seconds": self.scan_duration_seconds,
                "iac_types": [t.value for t in self.iac_types],
            },
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
        }
