"""Security AI Platform — Core orchestration engine.

Unifies SAST, DAST, secret scanning, CVE fix engine, compliance checking,
SIEM log aggregation, and a dashboard into a single security intelligence platform.

Usage:
    from security_ai_platform.core.platform import SecurityAIPlatform

    platform = SecurityAIPlatform(worktree_path="/path/to/repo")
    result = platform.full_scan()
    print(result.summary)
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ScanMode(str, Enum):
    """Scan execution modes."""
    SAST_ONLY = "sast_only"
    DAST_ONLY = "dast_only"
    SECRETS_ONLY = "secrets_only"
    CVE_ONLY = "cve_only"
    COMPLIANCE_ONLY = "compliance_only"
    SIEM_ONLY = "siem_only"
    FULL = "full"


@dataclass
class PlatformConfig:
    """Global configuration for the Security AI Platform."""
    worktree_path: str = "."
    scan_mode: ScanMode = ScanMode.FULL
    enabled_scanners: list[str] = field(default_factory=lambda: [
        "semgrep", "trivy", "opa", "secret_scan", "cve_fix", "compliance", "siem"
    ])
    risk_threshold: float = 50.0
    block_on_critical: bool = True
    block_on_high_count: int = 5
    compliance_frameworks: list[str] = field(default_factory=lambda: [
        "SOC2", "ISO27001", "PCI_DSS", "HIPAA"
    ])
    siem_endpoint: str = ""
    siem_batch_size: int = 100
    verbose: bool = False
    output_format: str = "json"  # json, text, sarif

    def to_dict(self) -> dict[str, Any]:
        return {
            "worktree_path": self.worktree_path,
            "scan_mode": self.scan_mode.value,
            "enabled_scanners": self.enabled_scanners,
            "risk_threshold": self.risk_threshold,
            "block_on_critical": self.block_on_critical,
            "block_on_high_count": self.block_on_high_count,
            "compliance_frameworks": self.compliance_frameworks,
            "siem_endpoint": self.siem_endpoint,
            "siem_batch_size": self.siem_batch_size,
            "verbose": self.verbose,
            "output_format": self.output_format,
        }


@dataclass
class PlatformResult:
    """Aggregated result from a full platform scan."""
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str = ""
    sast_result: dict[str, Any] = field(default_factory=dict)
    secret_findings: list[dict[str, Any]] = field(default_factory=list)
    cve_fixes: list[dict[str, Any]] = field(default_factory=list)
    compliance_reports: dict[str, Any] = field(default_factory=dict)
    siem_status: dict[str, Any] = field(default_factory=dict)
    dashboard_url: str = ""
    total_findings: int = 0
    total_critical: int = 0
    total_high: int = 0
    total_medium: int = 0
    total_low: int = 0
    overall_risk_score: float = 0.0
    overall_pass_fail: str = "pass"
    gate_reasons: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "sast_result": self.sast_result,
            "secret_findings": self.secret_findings,
            "cve_fixes": self.cve_fixes,
            "compliance_reports": self.compliance_reports,
            "siem_status": self.siem_status,
            "dashboard_url": self.dashboard_url,
            "total_findings": self.total_findings,
            "total_critical": self.total_critical,
            "total_high": self.total_high,
            "total_medium": self.total_medium,
            "total_low": self.total_low,
            "overall_risk_score": self.overall_risk_score,
            "overall_pass_fail": self.overall_pass_fail,
            "gate_reasons": self.gate_reasons,
            "summary": self.summary,
        }


class SecurityAIPlatform:
    """Main orchestrator for the Security AI Platform.

    Coordinates all security modules and produces a unified PlatformResult.

    Example:
        platform = SecurityAIPlatform(config=PlatformConfig(worktree_path="."))
        result = platform.full_scan()
        if result.overall_pass_fail == "fail":
            block_deployment()
    """

    def __init__(self, config: PlatformConfig | None = None) -> None:
        self.config = config or PlatformConfig()
        self.worktree_path = Path(self.config.worktree_path).resolve()
        logger.info("SecurityAI Platform initialized for %s", self.worktree_path)

    def full_scan(self) -> PlatformResult:
        """Execute the full security scan pipeline.

        Runs all enabled scanners, aggregates findings, computes overall
        risk, and produces a unified PlatformResult.

        Returns:
            PlatformResult with complete scan outcome.
        """
        result = PlatformResult()
        logger.info("Starting full security scan (run_id=%s)", result.run_id)

        # Run SAST/DAST pipeline
        if any(s in self.config.enabled_scanners for s in ["semgrep", "trivy", "opa"]):
            result.sast_result = self._run_sast_pipeline()

        # Run secret scanning
        if "secret_scan" in self.config.enabled_scanners:
            result.secret_findings = self._run_secret_scan()

        # Run CVE fix engine
        if "cve_fix" in self.config.enabled_scanners:
            result.cve_fixes = self._run_cve_fix_engine()

        # Run compliance checks
        if "compliance" in self.config.enabled_scanners:
            result.compliance_reports = self._run_compliance_checks()

        # Run SIEM log aggregation
        if "siem" in self.config.enabled_scanners:
            result.siem_status = self._run_siem_aggregation()

        # Aggregate all findings
        self._aggregate_findings(result)

        # Evaluate overall gate
        self._evaluate_gate(result)

        # Build summary
        result.completed_at = datetime.now(timezone.utc).isoformat()
        result.summary = self._build_summary(result)

        logger.info("Scan complete: %s", result.summary)
        return result

    def _run_sast_pipeline(self) -> dict[str, Any]:
        """Run the SAST/DAST scan pipeline."""
        try:
            from src.security.sast_dast.scanner import ScanPipeline
            pipeline = ScanPipeline(worktree_path=str(self.worktree_path))
            scan_result = pipeline.run(triggered_by="platform")
            return scan_result.to_dict()
        except Exception as exc:
            logger.warning("SAST pipeline failed: %s", exc)
            return {"error": str(exc), "findings": [], "risk_score": 0.0}

    def _run_secret_scan(self) -> list[dict[str, Any]]:
        """Run the secret scanner."""
        try:
            from security_ai_platform.scanners import SecretScanner
            scanner = SecretScanner(worktree_path=str(self.worktree_path))
            findings = scanner.scan()
            return [f.to_dict() for f in findings]
        except Exception as exc:
            logger.warning("Secret scanner failed: %s", exc)
            return []

    def _run_cve_fix_engine(self) -> list[dict[str, Any]]:
        """Run the CVE fix engine."""
        try:
            from security_ai_platform.fix_engine import CVEFixEngine
            engine = CVEFixEngine(worktree_path=str(self.worktree_path))
            fixes = engine.analyze_and_fix()
            return [f.to_dict() for f in fixes]
        except Exception as exc:
            logger.warning("CVE fix engine failed: %s", exc)
            return []

    def _run_compliance_checks(self) -> dict[str, Any]:
        """Run compliance checks for configured frameworks."""
        try:
            from security_ai_platform.compliance import ComplianceChecker
            checker = ComplianceChecker(
                worktree_path=str(self.worktree_path),
                frameworks=self.config.compliance_frameworks,
            )
            reports = checker.check_all()
            return {name: r.to_dict() for name, r in reports.items()}
        except Exception as exc:
            logger.warning("Compliance checks failed: %s", exc)
            return {"error": str(exc)}

    def _run_siem_aggregation(self) -> dict[str, Any]:
        """Run SIEM log aggregation."""
        try:
            from security_ai_platform.siem.aggregator import SIEMAggregator
            aggregator = SIEMAggregator(
                worktree_path=str(self.worktree_path),
                endpoint=self.config.siem_endpoint,
                batch_size=self.config.siem_batch_size,
            )
            return aggregator.aggregate()
        except Exception as exc:
            logger.warning("SIEM aggregation failed: %s", exc)
            return {"error": str(exc)}

    def _aggregate_findings(self, result: PlatformResult) -> None:
        """Aggregate findings from all modules into totals."""
        # SAST findings
        sast_findings = result.sast_result.get("findings", [])
        result.total_findings += len(sast_findings)
        result.total_critical += sum(1 for f in sast_findings if f.get("severity") == "critical")
        result.total_high += sum(1 for f in sast_findings if f.get("severity") == "high")
        result.total_medium += sum(1 for f in sast_findings if f.get("severity") == "medium")
        result.total_low += sum(1 for f in sast_findings if f.get("severity") == "low")

        # Secret findings
        result.total_findings += len(result.secret_findings)
        for f in result.secret_findings:
            sev = f.get("severity", "medium")
            if sev == "critical":
                result.total_critical += 1
            elif sev == "high":
                result.total_high += 1
            elif sev == "medium":
                result.total_medium += 1
            else:
                result.total_low += 1

        # CVE findings (from fixes)
        result.total_findings += len(result.cve_fixes)
        for fix in result.cve_fixes:
            sev = fix.get("severity", "medium")
            if sev == "critical":
                result.total_critical += 1
            elif sev == "high":
                result.total_high += 1
            elif sev == "medium":
                result.total_medium += 1
            else:
                result.total_low += 1

        # Compute overall risk score
        result.overall_risk_score = self._compute_overall_risk(result)

    def _compute_overall_risk(self, result: PlatformResult) -> float:
        """Compute the overall risk score across all modules."""
        score = 0.0
        score += result.total_critical * 10.0
        score += result.total_high * 5.0
        score += result.total_medium * 2.0
        score += result.total_low * 0.5

        # Count amplification
        if result.total_findings > 10:
            score *= 1.0 + 0.05 * (result.total_findings - 10)

        # Compliance penalty
        for fw_name, fw_report in result.compliance_reports.items():
            if isinstance(fw_report, dict):
                compliance_score = fw_report.get("compliance_score", 100)
                if compliance_score < 70:
                    score += (70 - compliance_score) * 0.5

        return round(min(100.0, score), 2)

    def _evaluate_gate(self, result: PlatformResult) -> None:
        """Evaluate the overall security gate."""
        reasons: list[str] = []

        if self.config.block_on_critical and result.total_critical > 0:
            reasons.append(
                f"BLOCKED: {result.total_critical} critical finding(s) detected"
            )

        if result.total_high > self.config.block_on_high_count:
            reasons.append(
                f"BLOCKED: {result.total_high} high-severity findings exceed "
                f"threshold of {self.config.block_on_high_count}"
            )

        if result.overall_risk_score >= self.config.risk_threshold:
            reasons.append(
                f"BLOCKED: Overall risk score {result.overall_risk_score} "
                f"exceeds threshold {self.config.risk_threshold}"
            )

        # Check compliance gates
        for fw_name, fw_report in result.compliance_reports.items():
            if isinstance(fw_report, dict):
                passed = fw_report.get("passed", True)
                if not passed:
                    reasons.append(
                        f"BLOCKED: Compliance framework {fw_name} failed"
                    )

        if reasons:
            result.overall_pass_fail = "fail"
            result.gate_reasons = reasons
        else:
            result.overall_pass_fail = "pass"

    def _build_summary(self, result: PlatformResult) -> str:
        """Build a human-readable scan summary."""
        parts = [
            f"Security AI Platform scan complete",
            f"Run ID: {result.run_id}",
            f"Total findings: {result.total_findings}",
            f"  Critical: {result.total_critical}",
            f"  High: {result.total_high}",
            f"  Medium: {result.total_medium}",
            f"  Low: {result.total_low}",
            f"Overall risk score: {result.overall_risk_score}",
            f"Gate: {result.overall_pass_fail.upper()}",
        ]

        if result.gate_reasons:
            parts.append("Gate reasons:")
            for reason in result.gate_reasons:
                parts.append(f"  - {reason}")

        if result.cve_fixes:
            parts.append(f"CVE fixes suggested: {len(result.cve_fixes)}")

        if result.compliance_reports and "error" not in result.compliance_reports:
            parts.append("Compliance status:")
            for fw_name, fw_report in result.compliance_reports.items():
                if isinstance(fw_report, dict):
                    status = "PASS" if fw_report.get("passed", False) else "FAIL"
                    score = fw_report.get("compliance_score", "N/A")
                    parts.append(f"  {fw_name}: {status} (score: {score})")

        return ". ".join(parts)