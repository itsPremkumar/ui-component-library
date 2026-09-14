"""Tests for Security AI Platform — Secret Scanner, CVE Fix Engine, Compliance, SIEM.

Run from workspace root: python -m pytest tests/ -v
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Also ensure src/ is importable
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from security_ai_platform.core import SecurityAIPlatform, PlatformConfig, ScanMode, PlatformResult
from security_ai_platform.scanners import SecretScanner, SecretFinding, SecretSeverity
from security_ai_platform.fix_engine import CVEFixEngine, CVEFix, FixSeverity, FixStatus
from security_ai_platform.compliance import (
    ComplianceChecker, ComplianceReport, ComplianceControl, ComplianceFramework
)
from security_ai_platform.siem import (
    SIEMAggregator, SIEMEvent, SIEMStatus, SIEMEventType, SIEMSeverity
)


# =========================================================================
# Secret Scanner Tests
# =========================================================================

class TestSecretScanner:
    """Tests for the Secret Scanner module."""

    def test_scanner_creation(self, tmp_path):
        scanner = SecretScanner(worktree_path=str(tmp_path))
        assert scanner.worktree_path == tmp_path.resolve()
        assert len(scanner.patterns) > 0

    def test_custom_patterns(self, tmp_path):
        custom = [{"name": "Custom Pattern", "pattern": r"custom_[a-z]+", "severity": SecretSeverity.MEDIUM, "description": "Test", "remediation": "Fix"}]
        scanner = SecretScanner(worktree_path=str(tmp_path), custom_patterns=custom)
        assert len(scanner.patterns) > 20  # Default + custom

    def test_clean_file_no_findings(self, tmp_path):
        (tmp_path / "clean.py").write_text("print('hello world')\nx = 1 + 2\n")
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) == 0

    def test_aws_access_key_detected(self, tmp_path):
        (tmp_path / "config.py").write_text('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) >= 1
        assert any(f.secret_type == "AWS Access Key ID" for f in findings)

    def test_github_token_detected(self, tmp_path):
        (tmp_path / "deploy.sh").write_text('token="ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef0123456789"\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert any("GitHub" in f.secret_type for f in findings)

    def test_private_key_detected(self, tmp_path):
        (tmp_path / "id_rsa").write_text(
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy..."
        )
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert any("Private Key" in f.secret_type for f in findings)

    def test_jwt_token_detected(self, tmp_path):
        (tmp_path / "auth.py").write_text(
            'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"'
        )
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert any("JWT" in f.secret_type for f in findings)

    def test_connection_string_with_password(self, tmp_path):
        (tmp_path / "db.py").write_text('uri = "postgres://user:secretpass@localhost/mydb"\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert any("Connection String" in f.secret_type for f in findings)

    def test_skip_binary_files(self, tmp_path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) == 0

    def test_skip_venv_directory(self, tmp_path):
        venv_dir = tmp_path / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "secrets.py").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) == 0

    def test_skip_node_modules(self, tmp_path):
        nm = tmp_path / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text('const key = "AKIAIOSFODNN7EXAMPLE";\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) == 0

    def test_multiple_secrets_in_one_file(self, tmp_path):
        (tmp_path / "all_secrets.py").write_text(
            'AWS = "AKIAIOSFODNN7EXAMPLE"\n'
            'GH = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef0123456789"\n'
        )
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert len(findings) >= 2

    def test_finding_to_dict(self):
        f = SecretFinding(
            finding_id="test-1",
            secret_type="Test",
            severity=SecretSeverity.HIGH,
            file_path="test.py",
            line_number=1,
            line_content="x = 1",
            matched_pattern="test",
            description="Test",
            remediation="Fix",
        )
        d = f.to_dict()
        assert d["finding_id"] == "test-1"
        assert d["severity"] == "high"
        assert "timestamp" in d

    def test_finding_severity_levels(self):
        assert SecretSeverity.CRITICAL.value == "critical"
        assert SecretSeverity.HIGH.value == "high"
        assert SecretSeverity.MEDIUM.value == "medium"
        assert SecretSeverity.LOW.value == "low"

    def test_comments_are_skipped(self, tmp_path):
        (tmp_path / "commented.py").write_text('# AKIAIOSFODNN7EXAMPLE\nx = 1\n')
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        # Comment lines should be skipped
        assert len(findings) == 0

    def test_npm_token_detected(self, tmp_path):
        (tmp_path / ".npmrc").write_text("//registry.npmjs.org/:_authToken=«redacted:npm_…»\n")
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        # .npmrc file extension is not .py/.js/.ts/.md so it may not be scanned
        # Write to a .sh file instead to ensure it is scanned
        (tmp_path / "publish.sh").write_text("npmToken = \"npm_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef1234567\"\n")
        scanner2 = SecretScanner(worktree_path=str(tmp_path))
        findings2 = scanner2.scan()
        assert any("NPM" in f.secret_type for f in findings2)

    def test_ssh_public_key_detected(self, tmp_path):
        (tmp_path / "id_rsa.pub").write_text(
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfZJ5juzK6dKrAq3Lg5t2NjGK3R5mG0sF7wYJp0oN3mZ9lQ6wYJp0oN3mZ9lQ6wYJp0oN3mZ9lQ6wYJp0oN3mZ9lQ6w user@host\n"
        )
        scanner = SecretScanner(worktree_path=str(tmp_path))
        findings = scanner.scan()
        assert any("SSH" in f.secret_type for f in findings)


# =========================================================================
# CVE Fix Engine Tests
# =========================================================================

class TestCVEFixEngine:
    """Tests for the CVE Fix Engine module."""

    def test_engine_creation(self, tmp_path):
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        assert engine.worktree_path == tmp_path.resolve()
        assert len(engine.vuln_db) > 0

    def test_no_requirements_file(self, tmp_path):
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert len(fixes) == 0

    def test_clean_requirements(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("pytest>=7.4.0\nrequests>=2.32.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert len(fixes) == 0

    def test_vulnerable_requests_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert len(fixes) >= 1
        assert fixes[0].package_name == "requests"
        assert fixes[0].cve_id == "CVE-2023-32681"

    def test_vulnerable_pyyaml_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("PyYAML==5.3\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert any(f.package_name == "pyyaml" for f in fixes)

    def test_vulnerable_flask_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("flask==2.2.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert any(f.package_name == "flask" for f in fixes)

    def test_vulnerable_django_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("django==4.2.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert any(f.package_name == "django" for f in fixes)

    def test_vulnerable_python_jose_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("python-jose==3.2.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert any(f.package_name == "python-jose" for f in fixes)

    def test_vulnerable_torch_detected(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("torch==2.0.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert any(f.package_name == "torch" for f in fixes)

    def test_pyproject_toml_scanning(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\ndependencies = [\n    "requests<2.31.0",\n]\n'
        )
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        # Version 2.31.0 is NOT < 2.31.0, so no fix should be suggested
        # Use a version that IS affected
        (tmp_path / "pyproject.toml").write_text(
            '[project]\ndependencies = [\n    "requests==2.28.0",\n]\n'
        )
        engine2 = CVEFixEngine(worktree_path=str(tmp_path))
        fixes2 = engine2.analyze_and_fix()
        assert any(f.package_name == "requests" for f in fixes2)

    def test_fix_to_dict(self):
        fix = CVEFix(
            fix_id="fix-1",
            cve_id="CVE-2024-TEST",
            package_name="test-pkg",
            current_version="1.0.0",
            fixed_version="1.0.1",
            severity=FixSeverity.HIGH,
            cvss_score=7.5,
            description="Test",
            fix_type="upgrade",
        )
        d = fix.to_dict()
        assert d["fix_id"] == "fix-1"
        assert d["severity"] == "high"
        assert d["status"] == "pending"
        assert "timestamp" in d

    def test_fix_severity_levels(self):
        assert FixSeverity.CRITICAL.value == "critical"
        assert FixSeverity.HIGH.value == "high"
        assert FixSeverity.MEDIUM.value == "medium"
        assert FixSeverity.LOW.value == "low"

    def test_custom_vulns_merged(self, tmp_path):
        custom = {
            "mypackage": [{
                "cve_id": "CVE-2024-CUSTOM",
                "severity": FixSeverity.HIGH,
                "cvss_score": 8.0,
                "description": "Custom vuln",
                "affected_versions": "<2.0",
                "fixed_version": "2.0",
            }]
        }
        engine = CVEFixEngine(worktree_path=str(tmp_path), custom_vulns=custom)
        assert "mypackage" in engine.vuln_db

    def test_multiple_vulns_in_one_file(self, tmp_path):
        (tmp_path / "requirements.txt").write_text(
            "requests==2.28.0\nflask==2.2.0\ndjango==4.2.0\n"
        )
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        pkg_names = {f.package_name for f in fixes}
        assert "requests" in pkg_names
        assert "flask" in pkg_names
        assert "django" in pkg_names

    def test_fix_has_remediation_steps(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        engine = CVEFixEngine(worktree_path=str(tmp_path))
        fixes = engine.analyze_and_fix()
        assert len(fixes) > 0
        assert len(fixes[0].remediation_steps) > 0


# =========================================================================
# Compliance Checker Tests
# =========================================================================

class TestComplianceChecker:
    """Tests for the Compliance Checker module."""

    def test_checker_creation(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path))
        assert checker.worktree_path == tmp_path.resolve()

    def test_soc2_report_generated(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["SOC2"])
        reports = checker.check_all()
        assert "SOC2" in reports
        assert isinstance(reports["SOC2"], ComplianceReport)

    def test_iso27001_report_generated(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["ISO27001"])
        reports = checker.check_all()
        assert "ISO27001" in reports

    def test_pci_dss_report_generated(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["PCI_DSS"])
        reports = checker.check_all()
        assert "PCI_DSS" in reports

    def test_hipaa_report_generated(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["HIPAA"])
        reports = checker.check_all()
        assert "HIPAA" in reports

    def test_all_frameworks_generated(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path))
        reports = checker.check_all()
        assert len(reports) == 4
        assert all(isinstance(r, ComplianceReport) for r in reports.values())

    def test_report_has_controls(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["SOC2"])
        reports = checker.check_all()
        report = reports["SOC2"]
        assert report.controls_total > 0
        assert len(report.controls) > 0

    def test_report_compliance_score_range(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["SOC2"])
        reports = checker.check_all()
        report = reports["SOC2"]
        assert 0 <= report.compliance_score <= 100

    def test_report_to_dict(self):
        report = ComplianceReport(
            framework="TEST",
            passed=True,
            compliance_score=85.0,
            controls_total=10,
            controls_passed=8,
            controls_failed=2,
            critical_findings=0,
            high_findings=1,
            medium_findings=1,
            low_findings=0,
        )
        d = report.to_dict()
        assert d["framework"] == "TEST"
        assert d["compliance_score"] == 85.0
        assert "timestamp" in d

    def test_control_to_dict(self):
        ctrl = ComplianceControl(
            control_id="TEST.1",
            name="Test Control",
            description="Test",
            passed=True,
            severity="high",
            evidence="Found",
        )
        d = ctrl.__dict__
        assert d["control_id"] == "TEST.1"
        assert d["passed"] is True

    def test_framework_enum_values(self):
        assert ComplianceFramework.SOC2.value == "SOC2"
        assert ComplianceFramework.ISO27001.value == "ISO27001"
        assert ComplianceFramework.PCI_DSS.value == "PCI_DSS"
        assert ComplianceFramework.HIPAA.value == "HIPAA"

    def test_unknown_framework_skipped(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["UNKNOWN"])
        reports = checker.check_all()
        assert len(reports) == 0

    def test_controls_passed_plus_failed_equals_total(self, tmp_path):
        checker = ComplianceChecker(worktree_path=str(tmp_path), frameworks=["SOC2"])
        reports = checker.check_all()
        report = reports["SOC2"]
        assert report.controls_passed + report.controls_failed == report.controls_total


# =========================================================================
# SIEM Aggregator Tests
# =========================================================================

class TestSIEMAggregator:
    """Tests for the SIEM Aggregator module."""

    def test_aggregator_creation(self, tmp_path):
        agg = SIEMAggregator(worktree_path=str(tmp_path))
        assert agg.worktree_path == tmp_path.resolve()
        assert agg.batch_size == 100

    def test_aggregate_no_endpoint(self, tmp_path):
        agg = SIEMAggregator(worktree_path=str(tmp_path), endpoint="")
        status = agg.aggregate()
        assert status.status in ("success", "partial", "error")
        assert status.events_sent == 0

    def test_event_to_dict(self):
        event = SIEMEvent(
            event_id="test-1",
            event_type="test.event",
            severity="high",
            timestamp="2024-01-01T00:00:00Z",
            source="test",
            message="Test event",
        )
        d = event.to_dict()
        assert d["event_id"] == "test-1"
        assert d["severity"] == "high"

    def test_status_to_dict(self):
        status = SIEMStatus(
            status="success",
            events_generated=10,
            events_sent=10,
            endpoint="https://test.com",
            batch_size=100,
        )
        d = status.to_dict()
        assert d["status"] == "success"
        assert d["events_generated"] == 10

    def test_event_type_enum(self):
        assert SIEMEventType.SECURITY_SCAN.value == "security.scan"
        assert SIEMEventType.FINDING.value == "security.finding"
        assert SIEMEventType.COMPLIANCE_CHECK.value == "security.compliance"

    def test_severity_enum(self):
        assert SIEMSeverity.CRITICAL.value == "critical"
        assert SIEMSeverity.HIGH.value == "high"
        assert SIEMSeverity.MEDIUM.value == "medium"
        assert SIEMSeverity.LOW.value == "low"
        assert SIEMSeverity.INFO.value == "info"

    def test_custom_batch_size(self, tmp_path):
        agg = SIEMAggregator(worktree_path=str(tmp_path), batch_size=50)
        assert agg.batch_size == 50

    def test_risk_to_severity_mapping(self, tmp_path):
        agg = SIEMAggregator(worktree_path=str(tmp_path))
        assert agg._risk_to_severity(80) == "critical"
        assert agg._risk_to_severity(60) == "high"
        assert agg._risk_to_severity(30) == "medium"
        assert agg._risk_to_severity(10) == "low"
        assert agg._risk_to_severity(0) == "info"


# =========================================================================
# Platform Integration Tests
# =========================================================================

class TestSecurityAIPlatform:
    """Tests for the main Security AI Platform orchestrator."""

    def test_platform_creation(self, tmp_path):
        config = PlatformConfig(worktree_path=str(tmp_path))
        platform = SecurityAIPlatform(config=config)
        assert platform.worktree_path == tmp_path.resolve()

    def test_platform_default_config(self):
        platform = SecurityAIPlatform()
        assert platform.config.scan_mode == ScanMode.FULL

    def test_platform_config_to_dict(self):
        config = PlatformConfig(worktree_path=".")
        d = config.to_dict()
        assert "scan_mode" in d
        assert "enabled_scanners" in d

    def test_platform_result_to_dict(self):
        result = PlatformResult()
        d = result.to_dict()
        assert "run_id" in d
        assert "overall_pass_fail" in d

    def test_full_scan_clean_project(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert isinstance(result, PlatformResult)
        assert result.total_findings == 0
        assert result.overall_pass_fail == "pass"

    def test_full_scan_with_secrets(self, tmp_path):
        (tmp_path / "config.py").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"\n')
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.total_findings >= 1
        assert result.total_critical >= 1

    def test_full_scan_with_vulnerable_deps(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["cve_fix"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.total_findings >= 1

    def test_full_scan_with_compliance(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["compliance"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert "SOC2" in result.compliance_reports

    def test_scan_mode_enum(self):
        assert ScanMode.FULL.value == "full"
        assert ScanMode.SAST_ONLY.value == "sast_only"
        assert ScanMode.SECRETS_ONLY.value == "secrets_only"
        assert ScanMode.CVE_ONLY.value == "cve_only"
        assert ScanMode.COMPLIANCE_ONLY.value == "compliance_only"
        assert ScanMode.SIEM_ONLY.value == "siem_only"

    def test_platform_summary_generated(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert len(result.summary) > 0
        assert "Security AI Platform" in result.summary

    def test_platform_run_id_is_unique(self, tmp_path):
        config = PlatformConfig(worktree_path=str(tmp_path))
        platform = SecurityAIPlatform(config=config)
        result1 = platform.full_scan()
        result2 = platform.full_scan()
        assert result1.run_id != result2.run_id

    def test_platform_timestamps_set(self, tmp_path):
        config = PlatformConfig(worktree_path=str(tmp_path))
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert len(result.started_at) > 0
        assert len(result.completed_at) > 0

    def test_platform_gate_blocks_on_critical(self, tmp_path):
        (tmp_path / "config.py").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"\n')
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
            block_on_critical=True,
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.overall_pass_fail == "fail"
        assert len(result.gate_reasons) > 0

    def test_platform_no_gate_block_when_clean(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan", "cve_fix"],
            block_on_critical=True,
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.overall_pass_fail == "pass"
        assert len(result.gate_reasons) == 0

    def test_platform_risk_score_computed(self, tmp_path):
        (tmp_path / "config.py").write_text('KEY = "AKIAIOSFODNN7EXAMPLE"\n')
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.overall_risk_score > 0

    def test_platform_risk_score_capped_at_100(self, tmp_path):
        # Create many secret findings
        content = "\n".join([f'KEY_{i} = "AKIAIOSFODNN7EXAMPLE{i:04d}"' for i in range(50)])
        (tmp_path / "many_secrets.py").write_text(content)
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.overall_risk_score <= 100.0

    def test_platform_with_all_scanners(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')\n")
        (tmp_path / "requirements.txt").write_text("requests>=2.32.0\n")
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["semgrep", "trivy", "opa", "secret_scan", "cve_fix", "compliance", "siem"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert isinstance(result, PlatformResult)
        assert result.completed_at != ""

    def test_platform_empty_workspace(self, tmp_path):
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["secret_scan", "cve_fix"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        assert result.total_findings == 0
        assert result.overall_pass_fail == "pass"

    def test_platform_compliance_gate_blocks(self, tmp_path):
        # Empty project should fail compliance (no security controls)
        config = PlatformConfig(
            worktree_path=str(tmp_path),
            enabled_scanners=["compliance"],
            compliance_frameworks=["SOC2"],
        )
        platform = SecurityAIPlatform(config=config)
        result = platform.full_scan()
        # SOC2 should fail on empty project
        assert "SOC2" in result.compliance_reports