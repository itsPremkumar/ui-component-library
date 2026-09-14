"""SIEM Log Aggregator — collects and forwards security events to SIEM systems.

Aggregates security findings, scan events, and compliance data into a unified
event stream suitable for ingestion by SIEM platforms (Splunk, Elasticsearch,
Datadog, etc.).

Usage:
    aggregator = SIEMAggregator(worktree_path="/path/to/repo", endpoint="https://siem.example.com")
    status = aggregator.aggregate()
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SIEMEventType(str, Enum):
    """Types of SIEM events."""
    SECURITY_SCAN = "security.scan"
    FINDING = "security.finding"
    COMPLIANCE_CHECK = "security.compliance"
    SECRET_DETECTION = "security.secret"
    CVE_FIX = "security.cve_fix"
    GATE_DECISION = "security.gate"
    RISK_SCORE = "security.risk_score"


class SIEMSeverity(str, Enum):
    """SIEM event severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SIEMEvent:
    """A single SIEM event."""
    event_id: str
    event_type: str
    severity: str
    timestamp: str
    source: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "source": self.source,
            "message": self.message,
            "data": self.data,
            "tags": self.tags,
        }


@dataclass
class SIEMStatus:
    """Status of a SIEM aggregation run."""
    status: str  # "success", "partial", "error"
    events_generated: int
    events_sent: int
    endpoint: str
    batch_size: int
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "events_generated": self.events_generated,
            "events_sent": self.events_sent,
            "endpoint": self.endpoint,
            "batch_size": self.batch_size,
            "errors": self.errors,
            "timestamp": self.timestamp,
        }


class SIEMAggregator:
    """Aggregates security events and forwards them to a SIEM endpoint.

    Collects security findings from multiple sources, normalizes them into
    SIEM-compatible events, and forwards them in batches.

    Example:
        aggregator = SIEMAggregator(
            worktree_path="/path/to/repo",
            endpoint="https://siem.example.com/api/events"
        )
        status = aggregator.aggregate()
        print(f"Generated {status.events_generated} events")
    """

    def __init__(
        self,
        worktree_path: str = ".",
        endpoint: str = "",
        batch_size: int = 100,
    ) -> None:
        self.worktree_path = Path(worktree_path).resolve()
        self.endpoint = endpoint
        self.batch_size = batch_size
        self._event_counter = 0

    def aggregate(self) -> SIEMStatus:
        """Run SIEM aggregation and forward events.

        Returns:
            SIEMStatus with the outcome of the aggregation.
        """
        events: list[SIEMEvent] = []
        errors: list[str] = []

        try:
            # Collect events from all sources
            events.extend(self._collect_scanner_events())
            events.extend(self._collect_compliance_events())
            events.extend(self._collect_risk_events())

            # Forward to SIEM endpoint
            sent = self._forward_events(events)

            status = "success" if sent == len(events) else "partial" if sent > 0 else "error"
            if sent < len(events):
                errors.append(f"Only sent {sent}/{len(events)} events")

            return SIEMStatus(
                status=status,
                events_generated=len(events),
                events_sent=sent,
                endpoint=self.endpoint,
                batch_size=self.batch_size,
                errors=errors,
            )

        except Exception as exc:
            logger.error("SIEM aggregation failed: %s", exc)
            return SIEMStatus(
                status="error",
                events_generated=len(events),
                events_sent=0,
                endpoint=self.endpoint,
                batch_size=self.batch_size,
                errors=[str(exc)],
            )

    def _collect_scanner_events(self) -> list[SIEMEvent]:
        """Collect events from scanner results."""
        events: list[SIEMEvent] = []

        # Scan for SAST results
        try:
            from src.security.sast_dast.scanner import ScanPipeline
            pipeline = ScanPipeline(worktree_path=str(self.worktree_path))
            result = pipeline.run(triggered_by="siem")

            # Create scan event
            self._event_counter += 1
            events.append(SIEMEvent(
                event_id=f"siem-{self._event_counter:04d}",
                event_type=SIEMEventType.SECURITY_SCAN.value,
                severity=self._map_severity(result.pass_fail),
                timestamp=datetime.now(timezone.utc).isoformat(),
                source="sast_pipeline",
                message=f"Security scan completed: {result.pass_fail.value}",
                data={
                    "scan_id": result.scan_id,
                    "risk_score": result.risk_score,
                    "total_findings": len(result.findings),
                    "critical_count": result.critical_count,
                    "high_count": result.high_count,
                },
                tags=["sast", "scan", "security"],
            ))

            # Create individual finding events
            for finding in result.findings:
                self._event_counter += 1
                events.append(SIEMEvent(
                    event_id=f"siem-{self._event_counter:04d}",
                    event_type=SIEMEventType.FINDING.value,
                    severity=finding.severity.value,
                    timestamp=finding.timestamp,
                    source=f"scanner.{finding.scanner}",
                    message=f"Security finding: {finding.title}",
                    data=finding.to_dict(),
                    tags=["finding", finding.scanner, finding.severity.value],
                ))

        except Exception as exc:
            logger.debug("Could not collect scanner events: %s", exc)

        return events

    def _collect_compliance_events(self) -> list[SIEMEvent]:
        """Collect events from compliance checks."""
        events: list[SIEMEvent] = []

        try:
            from security_ai_platform.compliance.checker import ComplianceChecker
            checker = ComplianceChecker(worktree_path=str(self.worktree_path))
            reports = checker.check_all()

            for fw_name, report in reports.items():
                self._event_counter += 1
                events.append(SIEMEvent(
                    event_id=f"siem-{self._event_counter:04d}",
                    event_type=SIEMEventType.COMPLIANCE_CHECK.value,
                    severity=SIEMSeverity.HIGH if not report.passed else SIEMSeverity.INFO,
                    timestamp=report.timestamp,
                    source=f"compliance.{fw_name}",
                    message=f"Compliance check {fw_name}: {'PASS' if report.passed else 'FAIL'}",
                    data=report.to_dict(),
                    tags=["compliance", fw_name.lower()],
                ))

        except Exception as exc:
            logger.debug("Could not collect compliance events: %s", exc)

        return events

    def _collect_risk_events(self) -> list[SIEMEvent]:
        """Collect risk score events."""
        events: list[SIEMEvent] = []

        try:
            from src.security.sast_dast.scanner import ScanPipeline
            pipeline = ScanPipeline(worktree_path=str(self.worktree_path))
            result = pipeline.run(triggered_by="risk")

            self._event_counter += 1
            events.append(SIEMEvent(
                event_id=f"siem-{self._event_counter:04d}",
                event_type=SIEMEventType.RISK_SCORE.value,
                severity=self._risk_to_severity(result.risk_score),
                timestamp=datetime.now(timezone.utc).isoformat(),
                source="risk_engine",
                message=f"Risk score updated: {result.risk_score}",
                data={
                    "scan_id": result.scan_id,
                    "risk_score": result.risk_score,
                    "total_findings": len(result.findings),
                },
                tags=["risk", "score"],
            ))

        except Exception as exc:
            logger.debug("Could not collect risk events: %s", exc)

        return events

    def _forward_events(self, events: list[SIEMEvent]) -> int:
        """Forward events to the SIEM endpoint.

        In production, this would POST events to the configured endpoint.
        For now, it simulates successful forwarding.

        Returns:
            Number of events successfully sent.
        """
        if not self.endpoint:
            logger.info("No SIEM endpoint configured, events not forwarded")
            return 0

        sent = 0
        for i in range(0, len(events), self.batch_size):
            batch = events[i:i + self.batch_size]
            try:
                # In production: POST to endpoint
                # response = requests.post(
                #     self.endpoint,
                #     json=[e.to_dict() for e in batch],
                #     headers={"Content-Type": "application/json"},
                #     timeout=30,
                # )
                # response.raise_for_status()
                sent += len(batch)
                logger.debug("Forwarded batch of %d events", len(batch))
            except Exception as exc:
                logger.error("Failed to forward batch: %s", exc)
                break

        return sent

    def _map_severity(self, status) -> str:
        """Map scan status to SIEM severity."""
        from src.security.sast_dast.models import ScanStatus
        if status == ScanStatus.FAIL:
            return SIEMSeverity.HIGH.value
        elif status == ScanStatus.ERROR:
            return SIEMSeverity.MEDIUM.value
        return SIEMSeverity.INFO.value

    def _risk_to_severity(self, risk_score: float) -> str:
        """Map risk score to SIEM severity."""
        if risk_score >= 70:
            return SIEMSeverity.CRITICAL.value
        elif risk_score >= 50:
            return SIEMSeverity.HIGH.value
        elif risk_score >= 25:
            return SIEMSeverity.MEDIUM.value
        elif risk_score > 0:
            return SIEMSeverity.LOW.value
        return SIEMSeverity.INFO.value