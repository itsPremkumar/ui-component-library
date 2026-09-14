"""Compliance Checker — evaluates security posture against regulatory frameworks.

Supports SOC 2, ISO 27001, PCI DSS, and HIPAA compliance frameworks.
Generates detailed compliance reports with pass/fail status and recommendations.

Usage:
    checker = ComplianceChecker(worktree_path="/path/to/repo", frameworks=["SOC2"])
    reports = checker.check_all()
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    PCI_DSS = "PCI_DSS"
    HIPAA = "HIPAA"


@dataclass
class ComplianceControl:
    """A single compliance control check."""
    control_id: str
    name: str
    description: str
    passed: bool
    severity: str  # "critical", "high", "medium", "low"
    evidence: str
    remediation: str = ""


@dataclass
class ComplianceReport:
    """Compliance report for a single framework."""
    framework: str
    passed: bool
    compliance_score: float  # 0-100
    controls_total: int
    controls_passed: int
    controls_failed: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    controls: list[ComplianceControl] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "passed": self.passed,
            "compliance_score": self.compliance_score,
            "controls_total": self.controls_total,
            "controls_passed": self.controls_passed,
            "controls_failed": self.controls_failed,
            "critical_findings": self.critical_findings,
            "high_findings": self.high_findings,
            "medium_findings": self.medium_findings,
            "low_findings": self.low_findings,
            "controls": [
                {
                    "control_id": c.control_id,
                    "name": c.name,
                    "description": c.description,
                    "passed": c.passed,
                    "severity": c.severity,
                    "evidence": c.evidence,
                    "remediation": c.remediation,
                }
                for c in self.controls
            ],
            "timestamp": self.timestamp,
        }


# SOC 2 Controls
_SOC2_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "CC6.1",
        "name": "Logical Access Controls",
        "description": "Implement logical access controls to prevent unauthorized access",
        "severity": "critical",
        "check": "access_controls",
    },
    {
        "id": "CC6.2",
        "name": "Authentication",
        "description": "Enforce multi-factor authentication for privileged access",
        "severity": "critical",
        "check": "mfa",
    },
    {
        "id": "CC6.3",
        "name": "Encryption at Rest",
        "description": "Encrypt sensitive data at rest using AES-256 or equivalent",
        "severity": "high",
        "check": "encryption_at_rest",
    },
    {
        "id": "CC6.4",
        "name": "Encryption in Transit",
        "description": "Encrypt data in transit using TLS 1.2+",
        "severity": "high",
        "check": "encryption_in_transit",
    },
    {
        "id": "CC6.5",
        "name": "Vulnerability Management",
        "description": "Regularly scan for and remediate vulnerabilities",
        "severity": "high",
        "check": "vulnerability_management",
    },
    {
        "id": "CC6.6",
        "name": "Audit Logging",
        "description": "Log security-relevant events and retain for analysis",
        "severity": "medium",
        "check": "audit_logging",
    },
    {
        "id": "CC6.7",
        "name": "Change Management",
        "description": "Implement formal change management process",
        "severity": "medium",
        "check": "change_management",
    },
    {
        "id": "CC6.8",
        "name": "Data Retention",
        "description": "Define and enforce data retention policies",
        "severity": "medium",
        "check": "data_retention",
    },
    {
        "id": "CC7.1",
        "name": "Security Monitoring",
        "description": "Implement continuous security monitoring",
        "severity": "high",
        "check": "security_monitoring",
    },
    {
        "id": "CC7.2",
        "name": "Incident Response",
        "description": "Maintain and test incident response plan",
        "severity": "high",
        "check": "incident_response",
    },
    {
        "id": "CC8.1",
        "name": "Risk Assessment",
        "description": "Conduct regular risk assessments",
        "severity": "medium",
        "check": "risk_assessment",
    },
    {
        "id": "CC8.2",
        "name": "Vendor Management",
        "description": "Assess security posture of third-party vendors",
        "severity": "medium",
        "check": "vendor_management",
    },
]

# ISO 27001 Controls
_ISO27001_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "A.5.1",
        "name": "Information Security Policies",
        "description": "Define and maintain information security policies",
        "severity": "high",
        "check": "security_policies",
    },
    {
        "id": "A.8.1",
        "name": "User Endpoint Devices",
        "description": "Protect information on user endpoint devices",
        "severity": "high",
        "check": "endpoint_protection",
    },
    {
        "id": "A.8.2",
        "name": "Privileged Access Rights",
        "description": "Manage privileged access rights",
        "severity": "critical",
        "check": "privileged_access",
    },
    {
        "id": "A.8.3",
        "name": "Information Access Restriction",
        "description": "Restrict access to information based on need-to-know",
        "severity": "high",
        "check": "access_restriction",
    },
    {
        "id": "A.8.5",
        "name": "Secure Authentication",
        "description": "Implement secure authentication mechanisms",
        "severity": "critical",
        "check": "secure_authentication",
    },
    {
        "id": "A.8.8",
        "name": "Management of Technical Vulnerabilities",
        "description": "Manage technical vulnerabilities systematically",
        "severity": "high",
        "check": "vulnerability_management",
    },
    {
        "id": "A.8.10",
        "name": "Deletion of Information",
        "description": "Securely delete information when no longer needed",
        "severity": "medium",
        "check": "data_deletion",
    },
    {
        "id": "A.8.11",
        "name": "Data Masking",
        "description": "Mask sensitive data in non-production environments",
        "severity": "medium",
        "check": "data_masking",
    },
    {
        "id": "A.8.12",
        "name": "Data Leakage Prevention",
        "description": "Prevent unauthorized data leakage",
        "severity": "high",
        "check": "dlp",
    },
    {
        "id": "A.8.15",
        "name": "Logging",
        "description": "Record and monitor security events",
        "severity": "medium",
        "check": "audit_logging",
    },
    {
        "id": "A.8.16",
        "name": "Monitoring Activities",
        "description": "Continuously monitor security events",
        "severity": "high",
        "check": "security_monitoring",
    },
    {
        "id": "A.5.23",
        "name": "Cloud Services Security",
        "description": "Secure use of cloud services",
        "severity": "high",
        "check": "cloud_security",
    },
]

# PCI DSS Controls
_PCI_DSS_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "1.1",
        "name": "Firewall Configuration",
        "description": "Install and maintain firewall configuration",
        "severity": "critical",
        "check": "firewall",
    },
    {
        "id": "2.1",
        "name": "Default Passwords",
        "description": "Change all default passwords and security parameters",
        "severity": "critical",
        "check": "default_passwords",
    },
    {
        "id": "3.1",
        "name": "Data Retention",
        "description": "Limit cardholder data retention to minimum necessary",
        "severity": "high",
        "check": "data_retention",
    },
    {
        "id": "3.4",
        "name": "PAN Storage Encryption",
        "description": "Render PAN unreadable anywhere it is stored",
        "severity": "critical",
        "check": "encryption_at_rest",
    },
    {
        "id": "4.1",
        "name": "Transmission Encryption",
        "description": "Use strong cryptography for transmission of cardholder data",
        "severity": "critical",
        "check": "encryption_in_transit",
    },
    {
        "id": "5.1",
        "name": "Anti-Virus",
        "description": "Deploy anti-virus software on all systems",
        "severity": "high",
        "check": "antivirus",
    },
    {
        "id": "6.1",
        "name": "Vulnerability Management",
        "description": "Establish process to identify security vulnerabilities",
        "severity": "high",
        "check": "vulnerability_management",
    },
    {
        "id": "6.2",
        "name": "Secure Development",
        "description": "Develop software based on secure coding guidelines",
        "severity": "high",
        "check": "secure_development",
    },
    {
        "id": "6.5",
        "name": "Address Common Vulnerabilities",
        "description": "Address common coding vulnerabilities in software development",
        "severity": "high",
        "check": "secure_coding",
    },
    {
        "id": "7.1",
        "name": "Access Control",
        "description": "Limit access to system components and cardholder data",
        "severity": "critical",
        "check": "access_controls",
    },
    {
        "id": "8.1",
        "name": "User Identification",
        "description": "Define and implement policies for user identification",
        "severity": "critical",
        "check": "user_identification",
    },
    {
        "id": "8.2",
        "name": "Authentication",
        "description": "Employ at least one method to authenticate users",
        "severity": "critical",
        "check": "secure_authentication",
    },
    {
        "id": "10.1",
        "name": "Audit Trails",
        "description": "Implement audit trails to link access to individual users",
        "severity": "high",
        "check": "audit_logging",
    },
    {
        "id": "11.1",
        "name": "Security Testing",
        "description": "Regularly test security systems and processes",
        "severity": "high",
        "check": "security_testing",
    },
    {
        "id": "12.1",
        "name": "Security Policy",
        "description": "Maintain a policy that addresses information security",
        "severity": "high",
        "check": "security_policies",
    },
]

# HIPAA Controls
_HIPAA_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "164.312(a)(1)",
        "name": "Access Control",
        "description": "Implement technical policies to allow access only to authorized persons",
        "severity": "critical",
        "check": "access_controls",
    },
    {
        "id": "164.312(a)(2)(i)",
        "name": "Unique User Identification",
        "description": "Assign a unique name for identifying and tracking user identity",
        "severity": "critical",
        "check": "user_identification",
    },
    {
        "id": "164.312(a)(2)(ii)",
        "name": "Emergency Access Procedure",
        "description": "Establish procedures for obtaining necessary ePHI during emergency",
        "severity": "high",
        "check": "emergency_access",
    },
    {
        "id": "164.312(a)(2)(iv)",
        "name": "Encryption and Decryption",
        "description": "Implement mechanism to encrypt and decrypt ePHI",
        "severity": "critical",
        "check": "encryption_at_rest",
    },
    {
        "id": "164.312(b)",
        "name": "Audit Controls",
        "description": "Implement hardware, software, and procedural mechanisms to record access",
        "severity": "high",
        "check": "audit_logging",
    },
    {
        "id": "164.312(c)(1)",
        "name": "Integrity",
        "description": "Protect ePHI from improper alteration or destruction",
        "severity": "high",
        "check": "data_integrity",
    },
    {
        "id": "164.312(d)",
        "name": "Person or Entity Authentication",
        "description": "Implement procedures to verify person or entity seeking access",
        "severity": "critical",
        "check": "secure_authentication",
    },
    {
        "id": "164.312(e)(1)",
        "name": "Transmission Security",
        "description": "Implement technical security measures to guard against unauthorized access",
        "severity": "critical",
        "check": "encryption_in_transit",
    },
    {
        "id": "164.308(a)(1)",
        "name": "Risk Analysis",
        "description": "Conduct accurate and thorough assessment of potential risks",
        "severity": "high",
        "check": "risk_assessment",
    },
    {
        "id": "164.308(a)(3)",
        "name": "Workforce Security",
        "description": "Implement procedures to ensure workforce members have appropriate access",
        "severity": "high",
        "check": "workforce_security",
    },
    {
        "id": "164.308(a)(4)",
        "name": "Information Access Management",
        "description": "Implement policies to authorize access to ePHI",
        "severity": "high",
        "check": "access_restriction",
    },
    {
        "id": "164.308(a)(5)",
        "name": "Security Awareness Training",
        "description": "Implement security awareness and training program",
        "severity": "medium",
        "check": "security_training",
    },
    {
        "id": "164.308(a)(7)",
        "name": "Contingency Plan",
        "description": "Establish and implement policies for responding to emergencies",
        "severity": "high",
        "check": "contingency_plan",
    },
    {
        "id": "164.310(a)(1)",
        "name": "Facility Access Controls",
        "description": "Implement policies to limit physical access to electronic information systems",
        "severity": "medium",
        "check": "physical_access",
    },
    {
        "id": "164.310(d)(1)",
        "name": "Device and Media Controls",
        "description": "Implement policies for receipt and removal of hardware and electronic media",
        "severity": "medium",
        "check": "media_controls",
    },
]


class ComplianceChecker:
    """Evaluates security posture against regulatory compliance frameworks.

    Supports SOC 2, ISO 27001, PCI DSS, and HIPAA frameworks.
    Generates detailed compliance reports with pass/fail status and recommendations.

    Example:
        checker = ComplianceChecker(
            worktree_path="/path/to/repo",
            frameworks=["SOC2", "ISO27001"]
        )
        reports = checker.check_all()
        for name, report in reports.items():
            print(f"{name}: {'PASS' if report.passed else 'FAIL'} ({report.compliance_score}%)")
    """

    def __init__(
        self,
        worktree_path: str = ".",
        frameworks: list[str] | None = None,
    ) -> None:
        self.worktree_path = Path(worktree_path).resolve()
        self.frameworks = frameworks or ["SOC2", "ISO27001", "PCI_DSS", "HIPAA"]

    def check_all(self) -> dict[str, ComplianceReport]:
        """Run compliance checks for all configured frameworks.

        Returns:
            Dictionary mapping framework name to ComplianceReport.
        """
        reports: dict[str, ComplianceReport] = {}

        for fw_name in self.frameworks:
            fw_upper = fw_name.upper()
            if fw_upper == "SOC2":
                reports["SOC2"] = self._check_soc2()
            elif fw_upper == "ISO27001":
                reports["ISO27001"] = self._check_iso27001()
            elif fw_upper in ("PCI_DSS", "PCIDSS", "PCI"):
                reports["PCI_DSS"] = self._check_pci_dss()
            elif fw_upper == "HIPAA":
                reports["HIPAA"] = self._check_hipaa()
            else:
                logger.warning("Unknown compliance framework: %s", fw_name)

        return reports

    def _check_soc2(self) -> ComplianceReport:
        """Run SOC 2 compliance checks."""
        return self._run_checks("SOC2", _SOC2_CONTROLS)

    def _check_iso27001(self) -> ComplianceReport:
        """Run ISO 27001 compliance checks."""
        return self._run_checks("ISO27001", _ISO27001_CONTROLS)

    def _check_pci_dss(self) -> ComplianceReport:
        """Run PCI DSS compliance checks."""
        return self._run_checks("PCI_DSS", _PCI_DSS_CONTROLS)

    def _check_hipaa(self) -> ComplianceReport:
        """Run HIPAA compliance checks."""
        return self._run_checks("HIPAA", _HIPAA_CONTROLS)

    def _run_checks(
        self,
        framework: str,
        controls: list[dict[str, Any]],
    ) -> ComplianceReport:
        """Run all controls for a framework and generate report."""
        results: list[ComplianceControl] = []

        for ctrl_def in controls:
            control = self._evaluate_control(ctrl_def)
            results.append(control)

        # Calculate score
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        score = round((passed / total) * 100, 1) if total > 0 else 0.0

        # Count findings by severity
        critical = sum(1 for r in results if not r.passed and r.severity == "critical")
        high = sum(1 for r in results if not r.passed and r.severity == "high")
        medium = sum(1 for r in results if not r.passed and r.severity == "medium")
        low = sum(1 for r in results if not r.passed and r.severity == "low")

        # Framework passes if score >= 80% and no critical failures
        overall_passed = score >= 80.0 and critical == 0

        return ComplianceReport(
            framework=framework,
            passed=overall_passed,
            compliance_score=score,
            controls_total=total,
            controls_passed=passed,
            controls_failed=failed,
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
            controls=results,
        )

    def _evaluate_control(self, ctrl_def: dict[str, Any]) -> ComplianceControl:
        """Evaluate a single compliance control."""
        check_name = ctrl_def["check"]
        check_method = getattr(self, f"_check_{check_name}", None)

        if check_method is None:
            return ComplianceControl(
                control_id=ctrl_def["id"],
                name=ctrl_def["name"],
                description=ctrl_def["description"],
                passed=False,
                severity=ctrl_def["severity"],
                evidence=f"Check '{check_name}' not implemented",
                remediation=f"Implement {check_name} check",
            )

        passed, evidence, remediation = check_method()
        return ComplianceControl(
            control_id=ctrl_def["id"],
            name=ctrl_def["name"],
            description=ctrl_def["description"],
            passed=passed,
            severity=ctrl_def["severity"],
            evidence=evidence,
            remediation=remediation,
        )

    # --- Individual control checks ---

    def _check_access_controls(self) -> tuple[bool, str, str]:
        """Check for access control implementation."""
        # Look for auth decorators, RBAC, etc.
        patterns = [
            r"@login_required",
            r"@permission_required",
            r"@roles_required",
            r"check_permission",
            r"has_permission",
            r"verify_access",
            r"rbac",
            r"acl",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Access controls found: {', '.join(found[:3])}", ""
        return False, "No access controls detected", "Implement access controls (RBAC/ABAC)"

    def _check_mfa(self) -> tuple[bool, str, str]:
        """Check for multi-factor authentication."""
        patterns = [
            r"mfa",
            r"multi.factor",
            r"two.factor",
            r"2fa",
            r"totp",
            r"otp",
            r"authenticator",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts", ".md"])
        if found:
            return True, f"MFA references found: {', '.join(found[:3])}", ""
        return False, "No MFA implementation detected", "Implement multi-factor authentication"

    def _check_encryption_at_rest(self) -> tuple[bool, str, str]:
        """Check for encryption at rest."""
        patterns = [
            r"encrypt",
            r"aes",
            r"cipher",
            r"cryptography",
            r"bcrypt",
            r"argon2",
            r"hashlib",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Encryption references found: {', '.join(found[:3])}", ""
        return False, "No encryption at rest detected", "Implement encryption at rest (AES-256)"

    def _check_encryption_in_transit(self) -> tuple[bool, str, str]:
        """Check for encryption in transit."""
        patterns = [
            r"https",
            r"tls",
            r"ssl",
            r"certificate",
            r"cert",
            r"https://",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts", ".yml", ".yaml", ".toml"])
        if found:
            return True, f"TLS/HTTPS references found: {', '.join(found[:3])}", ""
        return False, "No encryption in transit detected", "Enforce TLS 1.2+ for all communications"

    def _check_vulnerability_management(self) -> tuple[bool, str, str]:
        """Check for vulnerability management process."""
        patterns = [
            r"vulnerability",
            r"cve",
            r"security.scan",
            r"sast",
            r"dast",
            r"bandit",
            r"semgrep",
            r"trivy",
        ]
        found = self._search_patterns(patterns, [".py", ".yml", ".yaml", ".md", ".toml"])
        if found:
            return True, f"Vulnerability management found: {', '.join(found[:3])}", ""
        return False, "No vulnerability management detected", "Implement vulnerability scanning (SAST/DAST)"

    def _check_audit_logging(self) -> tuple[bool, str, str]:
        """Check for audit logging."""
        patterns = [
            r"audit",
            r"log\.info",
            r"log\.warning",
            r"logger",
            r"logging",
            r"structured.log",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Logging found: {', '.join(found[:3])}", ""
        return False, "No audit logging detected", "Implement structured audit logging"

    def _check_change_management(self) -> tuple[bool, str, str]:
        """Check for change management process."""
        # Look for CI/CD, PR templates, etc.
        has_cicd = (self.worktree_path / ".github" / "workflows").exists()
        has_pr_template = (self.worktree_path / ".github" / "pull_request_template.md").exists()
        if has_cicd or has_pr_template:
            evidence = []
            if has_cicd:
                evidence.append("CI/CD workflows found")
            if has_pr_template:
                evidence.append("PR template found")
            return True, "; ".join(evidence), ""
        return False, "No change management process detected", "Implement CI/CD and PR review process"

    def _check_data_retention(self) -> tuple[bool, str, str]:
        """Check for data retention policies."""
        patterns = [
            r"retention",
            r"ttl",
            r"expire",
            r"purge",
            r"cleanup",
            r"delete.old",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Data retention references found: {', '.join(found[:3])}", ""
        return False, "No data retention policy detected", "Define and implement data retention policies"

    def _check_security_monitoring(self) -> tuple[bool, str, str]:
        """Check for security monitoring."""
        patterns = [
            r"monitor",
            r"alert",
            r"siem",
            r"splunk",
            r"datadog",
            r"prometheus",
            r"grafana",
        ]
        found = self._search_patterns(patterns, [".py", ".yml", ".yaml", ".md"])
        if found:
            return True, f"Monitoring references found: {', '.join(found[:3])}", ""
        return False, "No security monitoring detected", "Implement security monitoring (SIEM/alerting)"

    def _check_incident_response(self) -> tuple[bool, str, str]:
        """Check for incident response plan."""
        patterns = [
            r"incident",
            r"response",
            r"on.call",
            r"pagerduty",
            r"opsgenie",
            r"runbook",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Incident response references found: {', '.join(found[:3])}", ""
        return False, "No incident response plan detected", "Create and test incident response plan"

    def _check_risk_assessment(self) -> tuple[bool, str, str]:
        """Check for risk assessment."""
        patterns = [
            r"risk",
            r"threat",
            r"assessment",
            r"stride",
            r"dread",
            r"risk_matrix",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Risk assessment references found: {', '.join(found[:3])}", ""
        return False, "No risk assessment detected", "Conduct regular risk assessments"

    def _check_vendor_management(self) -> tuple[bool, str, str]:
        """Check for vendor management."""
        patterns = [
            r"vendor",
            r"third.party",
            r"supplier",
            r"dependency",
            r"supply.chain",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Vendor management references found: {', '.join(found[:3])}", ""
        return False, "No vendor management detected", "Implement third-party vendor assessment"

    def _check_security_policies(self) -> tuple[bool, str, str]:
        """Check for security policies."""
        has_security_md = (self.worktree_path / "SECURITY.md").exists()
        has_policy = (self.worktree_path / "docs" / "security").exists()
        if has_security_md or has_policy:
            evidence = []
            if has_security_md:
                evidence.append("SECURITY.md found")
            if has_policy:
                evidence.append("Security docs found")
            return True, "; ".join(evidence), ""
        return False, "No security policies detected", "Create SECURITY.md and security documentation"

    def _check_endpoint_protection(self) -> tuple[bool, str, str]:
        """Check for endpoint protection."""
        patterns = [
            r"endpoint",
            r"antivirus",
            r"edr",
            r"mdm",
            r"device",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Endpoint protection references found: {', '.join(found[:3])}", ""
        return False, "No endpoint protection detected", "Implement endpoint protection (EDR/MDM)"

    def _check_privileged_access(self) -> tuple[bool, str, str]:
        """Check for privileged access management."""
        patterns = [
            r"privilege",
            r"admin",
            r"root",
            r"sudo",
            r"elevate",
            r"least.privilege",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Privileged access references found: {', '.join(found[:3])}", ""
        return False, "No privileged access management detected", "Implement least-privilege access model"

    def _check_access_restriction(self) -> tuple[bool, str, str]:
        """Check for information access restriction."""
        return self._check_access_controls()

    def _check_secure_authentication(self) -> tuple[bool, str, str]:
        """Check for secure authentication."""
        patterns = [
            r"auth",
            r"login",
            r"password",
            r"token",
            r"jwt",
            r"oauth",
            r"saml",
            r"openid",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Authentication references found: {', '.join(found[:3])}", ""
        return False, "No secure authentication detected", "Implement secure authentication (OAuth2/OIDC)"

    def _check_data_deletion(self) -> tuple[bool, str, str]:
        """Check for data deletion policies."""
        return self._check_data_retention()

    def _check_data_masking(self) -> tuple[bool, str, str]:
        """Check for data masking."""
        patterns = [
            r"mask",
            r"redact",
            r"anonymize",
            r"pseudonymize",
            r"tokenize",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Data masking references found: {', '.join(found[:3])}", ""
        return False, "No data masking detected", "Implement data masking for sensitive data"

    def _check_dlp(self) -> tuple[bool, str, str]:
        """Check for data loss prevention."""
        patterns = [
            r"dlp",
            r"leak",
            r"exfiltrat",
            r"data.loss",
            r"prevent",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"DLP references found: {', '.join(found[:3])}", ""
        return False, "No DLP detected", "Implement data loss prevention controls"

    def _check_cloud_security(self) -> tuple[bool, str, str]:
        """Check for cloud security."""
        patterns = [
            r"aws",
            r"azure",
            r"gcp",
            r"cloud",
            r"kubernetes",
            r"docker",
            r"container",
        ]
        found = self._search_patterns(patterns, [".py", ".yml", ".yaml", ".md"])
        if found:
            return True, f"Cloud security references found: {', '.join(found[:3])}", ""
        return False, "No cloud security detected", "Implement cloud security controls"

    def _check_firewall(self) -> tuple[bool, str, str]:
        """Check for firewall configuration."""
        patterns = [
            r"firewall",
            r"security.group",
            r"acl",
            r"network.acl",
            r"iptables",
            r"nftables",
        ]
        found = self._search_patterns(patterns, [".py", ".yml", ".yaml", ".md"])
        if found:
            return True, f"Firewall references found: {', '.join(found[:3])}", ""
        return False, "No firewall configuration detected", "Implement firewall rules"

    def _check_default_passwords(self) -> tuple[bool, str, str]:
        """Check for default password elimination."""
        # Look for hardcoded passwords
        patterns = [
            r"password\s*=\s*[\"'][^\"']+[\"']",
            r"admin\s*:\s*admin",
            r"root\s*:\s*root",
            r"default.*password",
        ]
        found = self._search_patterns(patterns, [".py", ".yml", ".yaml"])
        if found:
            return False, f"Default/hardcoded passwords found: {', '.join(found[:3])}", "Remove all default passwords"
        return True, "No default passwords detected", ""

    def _check_antivirus(self) -> tuple[bool, str, str]:
        """Check for anti-virus/anti-malware."""
        patterns = [
            r"antivirus",
            r"anti.virus",
            r"malware",
            r"clamav",
            r"crowdstrike",
            r"sentinel",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Anti-virus references found: {', '.join(found[:3])}", ""
        return False, "No anti-virus detected", "Deploy anti-virus/anti-malware solution"

    def _check_secure_development(self) -> tuple[bool, str, str]:
        """Check for secure development practices."""
        patterns = [
            r"secure.coding",
            r"owasp",
            r"sast",
            r"dast",
            r"code.review",
            r"security.review",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Secure development references found: {', '.join(found[:3])}", ""
        return False, "No secure development practices detected", "Implement secure coding guidelines"

    def _check_secure_coding(self) -> tuple[bool, str, str]:
        """Check for secure coding practices."""
        return self._check_secure_development()

    def _check_user_identification(self) -> tuple[bool, str, str]:
        """Check for user identification."""
        patterns = [
            r"user.id",
            r"username",
            r"email",
            r"account",
            r"identity",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"User identification references found: {', '.join(found[:3])}", ""
        return False, "No user identification detected", "Implement unique user identification"

    def _check_security_testing(self) -> tuple[bool, str, str]:
        """Check for security testing."""
        patterns = [
            r"security.test",
            r"penetration.test",
            r"pentest",
            r"security.scan",
            r"vulnerability.scan",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Security testing references found: {', '.join(found[:3])}", ""
        return False, "No security testing detected", "Implement regular security testing"

    def _check_emergency_access(self) -> tuple[bool, str, str]:
        """Check for emergency access procedures."""
        patterns = [
            r"emergency",
            r"break.glass",
            r"breakglass",
            r"urgent",
            r"escalat",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Emergency access references found: {', '.join(found[:3])}", ""
        return False, "No emergency access procedures detected", "Implement emergency access procedures"

    def _check_data_integrity(self) -> tuple[bool, str, str]:
        """Check for data integrity controls."""
        patterns = [
            r"integrity",
            r"checksum",
            r"hash",
            r"hmac",
            r"signature",
            r"verify",
        ]
        found = self._search_patterns(patterns, [".py", ".js", ".ts"])
        if found:
            return True, f"Data integrity references found: {', '.join(found[:3])}", ""
        return False, "No data integrity controls detected", "Implement data integrity verification"

    def _check_workforce_security(self) -> tuple[bool, str, str]:
        """Check for workforce security."""
        patterns = [
            r"background.check",
            r"training",
            r"awareness",
            r"security.training",
            r"onboard",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Workforce security references found: {', '.join(found[:3])}", ""
        return False, "No workforce security detected", "Implement security awareness training"

    def _check_security_training(self) -> tuple[bool, str, str]:
        """Check for security training."""
        return self._check_workforce_security()

    def _check_contingency_plan(self) -> tuple[bool, str, str]:
        """Check for contingency plan."""
        patterns = [
            r"backup",
            r"disaster",
            r"recovery",
            r"dr\.",
            r"contingency",
            r"bcp",
        ]
        found = self._search_patterns(patterns, [".py", ".md", ".yml", ".yaml"])
        if found:
            return True, f"Contingency plan references found: {', '.join(found[:3])}", ""
        return False, "No contingency plan detected", "Implement business continuity plan"

    def _check_physical_access(self) -> tuple[bool, str, str]:
        """Check for physical access controls."""
        patterns = [
            r"physical",
            r"badge",
            r"biometric",
            r"mantrap",
            r"cage",
        ]
        found = self._search_patterns(patterns, [".md", ".yml", ".yaml"])
        if found:
            return True, f"Physical access references found: {', '.join(found[:3])}", ""
        return False, "No physical access controls detected", "Implement physical access controls"

    def _check_media_controls(self) -> tuple[bool, str, str]:
        """Check for device and media controls."""
        patterns = [
            r"media",
            r"usb",
            r"removable",
            r"destroy",
            r"sanitize",
            r"wipe",
        ]
        found = self._search_patterns(patterns, [".md", ".yml", ".yaml"])
        if found:
            return True, f"Media control references found: {', '.join(found[:3])}", ""
        return False, "No media controls detected", "Implement media handling procedures"

    def _search_patterns(
        self,
        patterns: list[str],
        extensions: list[str],
    ) -> list[str]:
        """Search for patterns in files with given extensions."""
        found: list[str] = []
        try:
            for path in self.worktree_path.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in extensions:
                    continue
                # Skip common non-project directories
                parts = path.relative_to(self.worktree_path).parts
                if any(p in parts for p in [".git", ".venv", "node_modules", "__pycache__"]):
                    continue
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            if pattern not in found:
                                found.append(pattern)
                except OSError:
                    continue
        except OSError:
            pass
        return found