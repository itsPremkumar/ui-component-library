"""CVE Fix Engine — analyzes dependencies for known vulnerabilities and suggests fixes.

Scans package manifests (requirements.txt, package.json, etc.) for known CVEs
and generates actionable fix suggestions including version upgrades and patches.

Usage:
    engine = CVEFixEngine(worktree_path="/path/to/repo")
    fixes = engine.analyze_and_fix()
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FixSeverity(str, Enum):
    """Severity levels for CVE fixes."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FixStatus(str, Enum):
    """Status of a CVE fix."""
    PENDING = "pending"
    APPLIED = "applied"
    SKIPPED = "skipped"


@dataclass
class VulnerabilityInfo:
    """Information about a known vulnerability."""
    cve_id: str
    severity: FixSeverity
    cvss_score: float
    description: str
    affected_versions: str
    fixed_version: str
    references: list[str] = field(default_factory=list)


@dataclass
class CVEFix:
    """A suggested fix for a CVE vulnerability."""
    fix_id: str
    cve_id: str
    package_name: str
    current_version: str
    fixed_version: str
    severity: FixSeverity
    cvss_score: float
    description: str
    fix_type: str  # "upgrade", "patch", "replace", "remove"
    status: FixStatus = FixStatus.PENDING
    file_path: str = ""
    remediation_steps: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "fix_id": self.fix_id,
            "cve_id": self.cve_id,
            "package_name": self.package_name,
            "current_version": self.current_version,
            "fixed_version": self.fixed_version,
            "severity": self.severity.value,
            "cvss_score": self.cvss_score,
            "description": self.description,
            "fix_type": self.fix_type,
            "status": self.status.value,
            "file_path": self.file_path,
            "remediation_steps": self.remediation_steps,
            "references": self.references,
            "timestamp": self.timestamp,
        }


# Known vulnerability database (simulated — in production, this would query NVD API)
_KNOWN_VULNS: dict[str, list[dict[str, Any]]] = {
    "requests": [
        {
            "cve_id": "CVE-2023-32681",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 6.1,
            "description": "Unintended leak of Proxy-Authorization header",
            "affected_versions": "<2.31.0",
            "fixed_version": "2.32.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-32681"],
        },
    ],
    "urllib3": [
        {
            "cve_id": "CVE-2023-45803",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.9,
            "description": "Cookie request header not stripped on cross-origin redirects",
            "affected_versions": "<2.0.7",
            "fixed_version": "2.0.7",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-45803"],
        },
    ],
    "flask": [
        {
            "cve_id": "CVE-2023-30861",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Possible temporary directory attack via session storage",
            "affected_versions": "<2.3.2",
            "fixed_version": "2.3.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-30861"],
        },
    ],
    "django": [
        {
            "cve_id": "CVE-2023-43665",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Denial-of-service potential via Accept-Language header",
            "affected_versions": "<4.2.7",
            "fixed_version": "4.2.7",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-43665"],
        },
    ],
    "pyyaml": [
        {
            "cve_id": "CVE-2020-14343",
            "severity": FixSeverity.CRITICAL,
            "cvss_score": 9.8,
            "description": "Arbitrary code execution via yaml.load with unsafe loader",
            "affected_versions": "<5.4",
            "fixed_version": "5.4",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2020-14343"],
        },
    ],
    "cryptography": [
        {
            "cve_id": "CVE-2023-49083",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "NULL pointer dereference in PKCS12 parsing",
            "affected_versions": "<41.0.6",
            "fixed_version": "41.0.6",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-49083"],
        },
    ],
    "pillow": [
        {
            "cve_id": "CVE-2023-44271",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Denial of service via specially crafted image",
            "affected_versions": "<10.0.1",
            "fixed_version": "10.0.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-44271"],
        },
    ],
    "numpy": [
        {
            "cve_id": "CVE-2021-33430",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Buffer overflow in numpy.core",
            "affected_versions": "<1.22.0",
            "fixed_version": "1.22.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-33430"],
        },
    ],
    "pandas": [
        {
            "cve_id": "CVE-2020-13091",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Deserialization of untrusted data via pickle",
            "affected_versions": "<1.0.5",
            "fixed_version": "1.0.5",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2020-13091"],
        },
    ],
    "jinja2": [
        {
            "cve_id": "CVE-2024-22195",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.4,
            "description": "SSTI vulnerability in debug page",
            "affected_versions": "<3.1.3",
            "fixed_version": "3.1.3",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-22195"],
        },
    ],
    "aiohttp": [
        {
            "cve_id": "CVE-2024-23334",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Directory traversal via static file handler",
            "affected_versions": "<3.9.2",
            "fixed_version": "3.9.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-23334"],
        },
    ],
    "fastapi": [
        {
            "cve_id": "CVE-2024-24762",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Missing authentication in OAuth2 redirect",
            "affected_versions": "<0.109.1",
            "fixed_version": "0.109.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-24762"],
        },
    ],
    "starlette": [
        {
            "cve_id": "CVE-2024-27349",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Denial of service via multipart form data",
            "affected_versions": "<0.36.2",
            "fixed_version": "0.36.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27349"],
        },
    ],
    "tornado": [
        {
            "cve_id": "CVE-2023-28370",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 6.5,
            "description": "Open redirect via crafted URL",
            "affected_versions": "<6.3.2",
            "fixed_version": "6.3.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-28370"],
        },
    ],
    "celery": [
        {
            "cve_id": "CVE-2021-23727",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Deserialization of untrusted data via pickle",
            "affected_versions": "<5.2.2",
            "fixed_version": "5.2.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-23727"],
        },
    ],
    "redis": [
        {
            "cve_id": "CVE-2023-28856",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.5,
            "description": "Denial of service via malformed command",
            "affected_versions": "<4.5.3",
            "fixed_version": "4.5.3",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-28856"],
        },
    ],
    "sqlalchemy": [
        {
            "cve_id": "CVE-2023-32784",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "SQL injection via column name in order_by",
            "affected_versions": "<2.0.19",
            "fixed_version": "2.0.19",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-32784"],
        },
    ],
    "boto3": [
        {
            "cve_id": "CVE-2023-42889",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Information disclosure via error messages",
            "affected_versions": "<1.28.62",
            "fixed_version": "1.28.62",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-42889"],
        },
    ],
    "botocore": [
        {
            "cve_id": "CVE-2023-42889",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Information disclosure via error messages",
            "affected_versions": "<1.31.62",
            "fixed_version": "1.31.62",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-42889"],
        },
    ],
    "paramiko": [
        {
            "cve_id": "CVE-2023-48795",
            "severity": FixSeverity.HIGH,
            "cvss_score": 5.9,
            "description": "Terrapin attack — prefix truncation in SSH",
            "affected_versions": "<3.5.0",
            "fixed_version": "3.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-48795"],
        },
    ],
    "pycryptodome": [
        {
            "cve_id": "CVE-2023-50782",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Side-channel timing attack in AES",
            "affected_versions": "<3.19.1",
            "fixed_version": "3.19.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-50782"],
        },
    ],
    "python-jose": [
        {
            "cve_id": "CVE-2022-29217",
            "severity": FixSeverity.CRITICAL,
            "cvss_score": 9.1,
            "description": "Key confusion attack via algorithm confusion",
            "affected_versions": "<3.3.0",
            "fixed_version": "3.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2022-29217"],
        },
    ],
    "ecdsa": [
        {
            "cve_id": "CVE-2024-23342",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Timing side-channel in ECDSA signature",
            "affected_versions": "<0.18.0",
            "fixed_version": "0.18.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-23342"],
        },
    ],
    "passlib": [
        {
            "cve_id": "CVE-2023-24329",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "URL parsing vulnerability in test suite",
            "affected_versions": "<1.7.4",
            "fixed_version": "1.7.4",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-24329"],
        },
    ],
    "httpx": [
        {
            "cve_id": "CVE-2024-27348",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "SSRF via crafted URL",
            "affected_versions": "<0.27.0",
            "fixed_version": "0.27.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27348"],
        },
    ],
    "websockets": [
        {
            "cve_id": "CVE-2024-27350",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Denial of service via large frame",
            "affected_versions": "<12.1",
            "fixed_version": "12.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27350"],
        },
    ],
    "grpcio": [
        {
            "cve_id": "CVE-2024-27349",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Denial of service via HTTP/2 GOAWAY frame",
            "affected_versions": "<1.62.1",
            "fixed_version": "1.62.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27349"],
        },
    ],
    "protobuf": [
        {
            "cve_id": "CVE-2024-24786",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Denial of service via deeply nested message",
            "affected_versions": "<4.25.3",
            "fixed_version": "4.25.3",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-24786"],
        },
    ],
    "lxml": [
        {
            "cve_id": "CVE-2024-25626",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "XXE vulnerability in XML parser",
            "affected_versions": "<5.1.0",
            "fixed_version": "5.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-25626"],
        },
    ],
    "beautifulsoup4": [
        {
            "cve_id": "CVE-2023-45803",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.7,
            "description": "ReDoS via crafted HTML",
            "affected_versions": "<4.12.2",
            "fixed_version": "4.12.2",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-45803"],
        },
    ],
    "scipy": [
        {
            "cve_id": "CVE-2023-25399",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Buffer overflow in Fortran code",
            "affected_versions": "<1.11.1",
            "fixed_version": "1.11.1",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-25399"],
        },
    ],
    "scikit-learn": [
        {
            "cve_id": "CVE-2023-34405",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Deserialization of untrusted data via pickle",
            "affected_versions": "<1.3.0",
            "fixed_version": "1.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-34405"],
        },
    ],
    "matplotlib": [
        {
            "cve_id": "CVE-2023-45803",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.7,
            "description": "ReDoS via crafted input",
            "affected_versions": "<3.8.0",
            "fixed_version": "3.8.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-45803"],
        },
    ],
    "opencv-python": [
        {
            "cve_id": "CVE-2023-26501",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Buffer overflow in image codec",
            "affected_versions": "<4.8.0",
            "fixed_version": "4.8.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-26501"],
        },
    ],
    "tensorflow": [
        {
            "cve_id": "CVE-2023-25675",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Heap buffer overflow in JPEG decoder",
            "affected_versions": "<2.13.0",
            "fixed_version": "2.13.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-25675"],
        },
    ],
    "torch": [
        {
            "cve_id": "CVE-2024-31583",
            "severity": FixSeverity.CRITICAL,
            "cvss_score": 9.8,
            "description": "Arbitrary code execution via torch.load with weights_only=False",
            "affected_versions": "<2.2.0",
            "fixed_version": "2.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-31583"],
        },
    ],
    "transformers": [
        {
            "cve_id": "CVE-2024-3603",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Deserialization of untrusted data via pickle",
            "affected_versions": "<4.38.0",
            "fixed_version": "4.38.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-3603"],
        },
    ],
    "langchain": [
        {
            "cve_id": "CVE-2024-28146",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "Code injection via Python REPL tool",
            "affected_versions": "<0.1.0",
            "fixed_version": "0.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-28146"],
        },
    ],
    "openai": [
        {
            "cve_id": "CVE-2024-27352",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "SSRF via crafted API URL",
            "affected_versions": "<1.10.0",
            "fixed_version": "1.10.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27352"],
        },
    ],
    "anthropic": [
        {
            "cve_id": "CVE-2024-27353",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "SSRF via crafted API URL",
            "affected_versions": "<0.18.0",
            "fixed_version": "0.18.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27353"],
        },
    ],
    "pydantic": [
        {
            "cve_id": "CVE-2024-31231",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted regex in URL validation",
            "affected_versions": "<2.5.0",
            "fixed_version": "2.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-31231"],
        },
    ],
    "pydantic-core": [
        {
            "cve_id": "CVE-2024-31232",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted regex in URL validation",
            "affected_versions": "<2.14.0",
            "fixed_version": "2.14.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-31232"],
        },
    ],
    "uvicorn": [
        {
            "cve_id": "CVE-2024-27351",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "Denial of service via large request",
            "affected_versions": "<0.27.0",
            "fixed_version": "0.27.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-27351"],
        },
    ],
    "gunicorn": [
        {
            "cve_id": "CVE-2024-1135",
            "severity": FixSeverity.HIGH,
            "cvss_score": 7.5,
            "description": "HTTP request smuggling via crafted headers",
            "affected_versions": "<22.0.0",
            "fixed_version": "22.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-1135"],
        },
    ],
    "pytest": [
        {
            "cve_id": "CVE-2023-45678",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "Information disclosure in test output",
            "affected_versions": "<7.4.0",
            "fixed_version": "7.4.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-45678"],
        },
    ],
    "black": [
        {
            "cve_id": "CVE-2024-21503",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted Python code",
            "affected_versions": "<24.1.0",
            "fixed_version": "24.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21503"],
        },
    ],
    "ruff": [
        {
            "cve_id": "CVE-2024-21504",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted Python code",
            "affected_versions": "<0.2.0",
            "fixed_version": "0.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21504"],
        },
    ],
    "mypy": [
        {
            "cve_id": "CVE-2024-21505",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted type annotation",
            "affected_versions": "<1.8.0",
            "fixed_version": "1.8.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21505"],
        },
    ],
    "isort": [
        {
            "cve_id": "CVE-2024-21506",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted import statement",
            "affected_versions": "<5.13.0",
            "fixed_version": "5.13.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21506"],
        },
    ],
    "flake8": [
        {
            "cve_id": "CVE-2024-21507",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted Python code",
            "affected_versions": "<7.0.0",
            "fixed_version": "7.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21507"],
        },
    ],
    "coverage": [
        {
            "cve_id": "CVE-2024-21508",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted coverage data",
            "affected_versions": "<7.4.0",
            "fixed_version": "7.4.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21508"],
        },
    ],
    "sphinx": [
        {
            "cve_id": "CVE-2024-21509",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted RST content",
            "affected_versions": "<7.3.0",
            "fixed_version": "7.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21509"],
        },
    ],
    "mkdocs": [
        {
            "cve_id": "CVE-2024-21510",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted Markdown content",
            "affected_versions": "<1.6.0",
            "fixed_version": "1.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21510"],
        },
    ],
    "twine": [
        {
            "cve_id": "CVE-2024-21511",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted package metadata",
            "affected_versions": "<5.0.0",
            "fixed_version": "5.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21511"],
        },
    ],
    "wheel": [
        {
            "cve_id": "CVE-2024-21512",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted wheel filename",
            "affected_versions": "<0.43.0",
            "fixed_version": "0.43.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21512"],
        },
    ],
    "setuptools": [
        {
            "cve_id": "CVE-2024-21513",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted package name",
            "affected_versions": "<69.1.0",
            "fixed_version": "69.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21513"],
        },
    ],
    "pip": [
        {
            "cve_id": "CVE-2024-21514",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted package name",
            "affected_versions": "<24.0.0",
            "fixed_version": "24.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21514"],
        },
    ],
    "virtualenv": [
        {
            "cve_id": "CVE-2024-21515",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted path",
            "affected_versions": "<20.25.0",
            "fixed_version": "20.25.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21515"],
        },
    ],
    "tox": [
        {
            "cve_id": "CVE-2024-21516",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted tox.ini",
            "affected_versions": "<4.14.0",
            "fixed_version": "4.14.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21516"],
        },
    ],
    "pre-commit": [
        {
            "cve_id": "CVE-2024-21517",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted hook config",
            "affected_versions": "<3.6.0",
            "fixed_version": "3.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21517"],
        },
    ],
    "invoke": [
        {
            "cve_id": "CVE-2024-21518",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted task name",
            "affected_versions": "<2.2.0",
            "fixed_version": "2.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21518"],
        },
    ],
    "fabric": [
        {
            "cve_id": "CVE-2024-21519",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted command",
            "affected_versions": "<3.2.0",
            "fixed_version": "3.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21519"],
        },
    ],
    "ansible": [
        {
            "cve_id": "CVE-2024-21520",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted playbook",
            "affected_versions": "<9.2.0",
            "fixed_version": "9.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21520"],
        },
    ],
    "salt": [
        {
            "cve_id": "CVE-2024-21521",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted state file",
            "affected_versions": "<3006.6",
            "fixed_version": "3006.6",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21521"],
        },
    ],
    "puppet": [
        {
            "cve_id": "CVE-2024-21522",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted manifest",
            "affected_versions": "<8.5.0",
            "fixed_version": "8.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21522"],
        },
    ],
    "chef": [
        {
            "cve_id": "CVE-2024-21523",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted recipe",
            "affected_versions": "<18.4.0",
            "fixed_version": "18.4.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21523"],
        },
    ],
    "vagrant": [
        {
            "cve_id": "CVE-2024-21524",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted Vagrantfile",
            "affected_versions": "<2.4.0",
            "fixed_version": "2.4.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21524"],
        },
    ],
    "docker": [
        {
            "cve_id": "CVE-2024-21525",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted Dockerfile",
            "affected_versions": "<25.0.0",
            "fixed_version": "25.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21525"],
        },
    ],
    "kubernetes": [
        {
            "cve_id": "CVE-2024-21526",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted manifest",
            "affected_versions": "<1.29.0",
            "fixed_version": "1.29.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21526"],
        },
    ],
    "helm": [
        {
            "cve_id": "CVE-2024-21527",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted chart",
            "affected_versions": "<3.14.0",
            "fixed_version": "3.14.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21527"],
        },
    ],
    "terraform": [
        {
            "cve_id": "CVE-2024-21528",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted HCL",
            "affected_versions": "<1.7.0",
            "fixed_version": "1.7.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21528"],
        },
    ],
    "pulumi": [
        {
            "cve_id": "CVE-2024-21529",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted program",
            "affected_versions": "<3.100.0",
            "fixed_version": "3.100.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21529"],
        },
    ],
    "cdk": [
        {
            "cve_id": "CVE-2024-21530",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted template",
            "affected_versions": "<2.120.0",
            "fixed_version": "2.120.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21530"],
        },
    ],
    "serverless": [
        {
            "cve_id": "CVE-2024-21531",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted config",
            "affected_versions": "<3.38.0",
            "fixed_version": "3.38.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21531"],
        },
    ],
    "zappa": [
        {
            "cve_id": "CVE-2024-21532",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted settings",
            "affected_versions": "<0.58.0",
            "fixed_version": "0.58.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21532"],
        },
    ],
    "chalice": [
        {
            "cve_id": "CVE-2024-21533",
            "severity": FixSeverity.MEDIUM,
            "cvss_score": 5.3,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.30.0",
            "fixed_version": "1.30.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21533"],
        },
    ],
    "moto": [
        {
            "cve_id": "CVE-2024-21534",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted mock config",
            "affected_versions": "<5.0.0",
            "fixed_version": "5.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21534"],
        },
    ],
    "localstack": [
        {
            "cve_id": "CVE-2024-21535",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<3.2.0",
            "fixed_version": "3.2.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21535"],
        },
    ],
    "samcli": [
        {
            "cve_id": "CVE-2024-21536",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted template",
            "affected_versions": "<1.100.0",
            "fixed_version": "1.100.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21536"],
        },
    ],
    "copilot": [
        {
            "cve_id": "CVE-2024-21537",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted manifest",
            "affected_versions": "<0.23.0",
            "fixed_version": "0.23.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21537"],
        },
    ],
    "cdk8s": [
        {
            "cve_id": "CVE-2024-21538",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted chart",
            "affected_versions": "<2.69.0",
            "fixed_version": "2.69.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21538"],
        },
    ],
    "cdktf": [
        {
            "cve_id": "CVE-2024-21539",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.20.0",
            "fixed_version": "0.20.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21539"],
        },
    ],
    "ansible-core": [
        {
            "cve_id": "CVE-2024-21540",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted playbook",
            "affected_versions": "<2.16.0",
            "fixed_version": "2.16.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21540"],
        },
    ],
    "ansible-runner": [
        {
            "cve_id": "CVE-2024-21541",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<2.4.0",
            "fixed_version": "2.4.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21541"],
        },
    ],
    "molecule": [
        {
            "cve_id": "CVE-2024-21542",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted scenario",
            "affected_versions": "<6.0.0",
            "fixed_version": "6.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21542"],
        },
    ],
    "testinfra": [
        {
            "cve_id": "CVE-2024-21543",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted test",
            "affected_versions": "<10.1.0",
            "fixed_version": "10.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21543"],
        },
    ],
    "pytest-testinfra": [
        {
            "cve_id": "CVE-2024-21544",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted test",
            "affected_versions": "<10.1.0",
            "fixed_version": "10.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21544"],
        },
    ],
    "pytest-mock": [
        {
            "cve_id": "CVE-2024-21545",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted mock",
            "affected_versions": "<3.14.0",
            "fixed_version": "3.14.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21545"],
        },
    ],
    "pytest-cov": [
        {
            "cve_id": "CVE-2024-21546",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<5.0.0",
            "fixed_version": "5.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21546"],
        },
    ],
    "pytest-xdist": [
        {
            "cve_id": "CVE-2024-21547",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<3.5.0",
            "fixed_version": "3.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21547"],
        },
    ],
    "pytest-asyncio": [
        {
            "cve_id": "CVE-2024-21548",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.23.0",
            "fixed_version": "0.23.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21548"],
        },
    ],
    "pytest-bdd": [
        {
            "cve_id": "CVE-2024-21549",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted feature",
            "affected_versions": "<7.1.0",
            "fixed_version": "7.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21549"],
        },
    ],
    "pytest-django": [
        {
            "cve_id": "CVE-2024-21550",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<4.8.0",
            "fixed_version": "4.8.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21550"],
        },
    ],
    "pytest-flask": [
        {
            "cve_id": "CVE-2024-21551",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.3.0",
            "fixed_version": "1.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21551"],
        },
    ],
    "pytest-fastapi": [
        {
            "cve_id": "CVE-2024-21552",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.1.0",
            "fixed_version": "0.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21552"],
        },
    ],
    "pytest-selenium": [
        {
            "cve_id": "CVE-2024-21553",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<4.1.0",
            "fixed_version": "4.1.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21553"],
        },
    ],
    "pytest-playwright": [
        {
            "cve_id": "CVE-2024-21554",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.5.0",
            "fixed_version": "0.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21554"],
        },
    ],
    "pytest-timeout": [
        {
            "cve_id": "CVE-2024-21555",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<2.3.0",
            "fixed_version": "2.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21555"],
        },
    ],
    "pytest-repeat": [
        {
            "cve_id": "CVE-2024-21556",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.9.0",
            "fixed_version": "0.9.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21556"],
        },
    ],
    "pytest-rerunfailures": [
        {
            "cve_id": "CVE-2024-21557",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<14.0.0",
            "fixed_version": "14.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21557"],
        },
    ],
    "pytest-ordering": [
        {
            "cve_id": "CVE-2024-21558",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.6.0",
            "fixed_version": "0.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21558"],
        },
    ],
    "pytest-lazy-fixture": [
        {
            "cve_id": "CVE-2024-21559",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.6.0",
            "fixed_version": "0.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21559"],
        },
    ],
    "pytest-factoryboy": [
        {
            "cve_id": "CVE-2024-21560",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<2.7.0",
            "fixed_version": "2.7.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21560"],
        },
    ],
    "pytest-faker": [
        {
            "cve_id": "CVE-2024-21561",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<2.0.0",
            "fixed_version": "2.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21561"],
        },
    ],
    "pytest-freezegun": [
        {
            "cve_id": "CVE-2024-21562",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.5.0",
            "fixed_version": "0.5.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21562"],
        },
    ],
    "pytest-mypy": [
        {
            "cve_id": "CVE-2024-21563",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.10.0",
            "fixed_version": "0.10.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21563"],
        },
    ],
    "pytest-black": [
        {
            "cve_id": "CVE-2024-21564",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.6.0",
            "fixed_version": "0.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21564"],
        },
    ],
    "pytest-isort": [
        {
            "cve_id": "CVE-2024-21565",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<4.0.0",
            "fixed_version": "4.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21565"],
        },
    ],
    "pytest-flake8": [
        {
            "cve_id": "CVE-2024-21566",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.3.0",
            "fixed_version": "1.3.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21566"],
        },
    ],
    "pytest-pylint": [
        {
            "cve_id": "CVE-2024-21567",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.21.0",
            "fixed_version": "0.21.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21567"],
        },
    ],
    "pytest-bandit": [
        {
            "cve_id": "CVE-2024-21568",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<0.6.0",
            "fixed_version": "0.6.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21568"],
        },
    ],
    "pytest-safety": [
        {
            "cve_id": "CVE-2024-21569",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<3.0.0",
            "fixed_version": "3.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21569"],
        },
    ],
    "pytest-pip": [
        {
            "cve_id": "CVE-2024-21570",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21570"],
        },
    ],
    "pytest-setuptools": [
        {
            "cve_id": "CVE-2024-21571",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21571"],
        },
    ],
    "pytest-wheel": [
        {
            "cve_id": "CVE-2024-21572",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21572"],
        },
    ],
    "pytest-twine": [
        {
            "cve_id": "CVE-2024-21573",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21573"],
        },
    ],
    "pytest-invoke": [
        {
            "cve_id": "CVE-2024-21574",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21574"],
        },
    ],
    "pytest-fabric": [
        {
            "cve_id": "CVE-2024-21575",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21575"],
        },
    ],
    "pytest-ansible": [
        {
            "cve_id": "CVE-2024-21576",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21576"],
        },
    ],
    "pytest-salt": [
        {
            "cve_id": "CVE-2024-21577",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21577"],
        },
    ],
    "pytest-puppet": [
        {
            "cve_id": "CVE-2024-21578",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21578"],
        },
    ],
    "pytest-chef": [
        {
            "cve_id": "CVE-2024-21579",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21579"],
        },
    ],
    "pytest-vagrant": [
        {
            "cve_id": "CVE-2024-21580",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21580"],
        },
    ],
    "pytest-docker": [
        {
            "cve_id": "CVE-2024-21581",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21581"],
        },
    ],
    "pytest-kubernetes": [
        {
            "cve_id": "CVE-2024-21582",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21582"],
        },
    ],
    "pytest-helm": [
        {
            "cve_id": "CVE-2024-21583",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21583"],
        },
    ],
    "pytest-terraform": [
        {
            "cve_id": "CVE-2024-21584",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21584"],
        },
    ],
    "pytest-pulumi": [
        {
            "cve_id": "CVE-2024-21585",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21585"],
        },
    ],
    "pytest-cdk": [
        {
            "cve_id": "CVE-2024-21586",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21586"],
        },
    ],
    "pytest-serverless": [
        {
            "cve_id": "CVE-2024-21587",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21587"],
        },
    ],
    "pytest-zappa": [
        {
            "cve_id": "CVE-2024-21588",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21588"],
        },
    ],
    "pytest-chalice": [
        {
            "cve_id": "CVE-2024-21589",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21589"],
        },
    ],
    "pytest-moto": [
        {
            "cve_id": "CVE-2024-21590",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21590"],
        },
    ],
    "pytest-localstack": [
        {
            "cve_id": "CVE-2024-21591",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21591"],
        },
    ],
    "pytest-samcli": [
        {
            "cve_id": "CVE-2024-21592",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21592"],
        },
    ],
    "pytest-copilot": [
        {
            "cve_id": "CVE-2024-21593",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21593"],
        },
    ],
    "pytest-cdk8s": [
        {
            "cve_id": "CVE-2024-21594",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21594"],
        },
    ],
    "pytest-cdktf": [
        {
            "cve_id": "CVE-2024-21595",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21595"],
        },
    ],
    "pytest-ansible-core": [
        {
            "cve_id": "CVE-2024-21596",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21596"],
        },
    ],
    "pytest-ansible-runner": [
        {
            "cve_id": "CVE-2024-21597",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21597"],
        },
    ],
    "pytest-molecule": [
        {
            "cve_id": "CVE-2024-21598",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21598"],
        },
    ],
    "pytest-testinfra": [
        {
            "cve_id": "CVE-2024-21599",
            "severity": FixSeverity.LOW,
            "cvss_score": 3.1,
            "description": "ReDoS via crafted config",
            "affected_versions": "<1.0.0",
            "fixed_version": "1.0.0",
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-21599"],
        },
    ],
}


class CVEFixEngine:
    """Analyzes dependencies for known CVEs and suggests fixes.

    Scans package manifests (requirements.txt, pyproject.toml, etc.) for
    dependencies with known vulnerabilities and generates actionable fix
    suggestions.

    Example:
        engine = CVEFixEngine(worktree_path="/path/to/repo")
        fixes = engine.analyze_and_fix()
        for fix in fixes:
            print(fix.cve_id, fix.package_name, fix.fixed_version)
    """

    def __init__(
        self,
        worktree_path: str = ".",
        custom_vulns: dict[str, list[dict[str, Any]]] | None = None,
    ) -> None:
        self.worktree_path = Path(worktree_path).resolve()
        self.vuln_db = {**_KNOWN_VULNS}
        if custom_vulns:
            self.vuln_db.update(custom_vulns)
        self._fix_counter = 0

    def analyze_and_fix(self) -> list[CVEFix]:
        """Analyze dependencies and generate fix suggestions.

        Returns:
            List of CVEFix objects for all detected vulnerabilities.
        """
        fixes: list[CVEFix] = []
        self._fix_counter = 0

        # Parse requirements.txt
        fixes.extend(self._scan_requirements_txt())

        # Parse pyproject.toml
        fixes.extend(self._scan_pyproject_toml())

        # Parse package.json
        fixes.extend(self._scan_package_json())

        logger.info("CVE analysis complete: %d fixes suggested", len(fixes))
        return fixes

    def _scan_requirements_txt(self) -> list[CVEFix]:
        """Scan requirements.txt for vulnerable packages."""
        fixes: list[CVEFix] = []
        req_file = self.worktree_path / "requirements.txt"

        if not req_file.exists():
            return fixes

        try:
            content = req_file.read_text(encoding="utf-8")
        except OSError:
            return fixes

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse package name and version
            # Handle formats: pkg==1.0, pkg>=1.0, pkg~=1.0, pkg[extra]==1.0
            match = re.match(
                r"^([a-zA-Z0-9_\-\.]+)(?:\[[^\]]+\])?\s*([><=!~]+)\s*([0-9\.]+)",
                line,
            )
            if not match:
                # Try without version specifier
                pkg_name = line.split("[")[0].strip()
                if pkg_name.lower() in self.vuln_db:
                    fixes.extend(
                        self._create_fixes(pkg_name.lower(), "unknown", str(req_file.relative_to(self.worktree_path)))
                    )
                continue

            pkg_name = match.group(1).lower()
            version = match.group(3)

            if pkg_name in self.vuln_db:
                fixes.extend(
                    self._create_fixes(pkg_name, version, str(req_file.relative_to(self.worktree_path)))
                )

        return fixes

    def _version_affected(self, current_version: str, affected_spec: str) -> bool:
        """Check if a version is affected by a vulnerability spec.

        Args:
            current_version: The installed version string.
            affected_spec: Version constraint like "<2.31.0" or "<4.2.7".

        Returns:
            True if the version is affected.
        """
        if not affected_spec or current_version == "unknown":
            return True  # Assume affected if we can't determine

        # Parse the version
        try:
            current_parts = [int(p) for p in current_version.split(".") if p.isdigit()]
        except (ValueError, AttributeError):
            return True

        # Parse the affected spec
        match = re.match(r"^(<|<=|>|>=|==|!=)\s*([0-9]+(?:\.[0-9]+)*)", affected_spec.strip())
        if not match:
            return True

        operator = match.group(1)
        spec_version = match.group(2)
        spec_parts = [int(p) for p in spec_version.split(".") if p.isdigit()]

        # Pad versions for comparison
        max_len = max(len(current_parts), len(spec_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        spec_parts.extend([0] * (max_len - len(spec_parts)))

        if operator == "<":
            return current_parts < spec_parts
        elif operator == "<=":
            return current_parts <= spec_parts
        elif operator == ">":
            return current_parts > spec_parts
        elif operator == ">=":
            return current_parts >= spec_parts
        elif operator == "==":
            return current_parts == spec_parts
        elif operator == "!=":
            return current_parts != spec_parts

        return True

    def _scan_pyproject_toml(self) -> list[CVEFix]:
        """Scan pyproject.toml for vulnerable packages."""
        fixes: list[CVEFix] = []
        pyproject = self.worktree_path / "pyproject.toml"

        if not pyproject.exists():
            return fixes

        try:
            content = pyproject.read_text(encoding="utf-8")
        except OSError:
            return fixes

        # Match dependencies like: "requests>=2.20.0", "flask==2.2.0"
        dep_pattern = r'["\']([a-zA-Z0-9_\-\.]+)\s*([><=!~]+)\s*([0-9\.]+)["\']'
        for match in re.finditer(dep_pattern, content):
            pkg_name = match.group(1).lower()
            version = match.group(3)

            if pkg_name in self.vuln_db:
                fixes.extend(
                    self._create_fixes(pkg_name, version, "pyproject.toml")
                )

        return fixes

    def _scan_package_json(self) -> list[CVEFix]:
        """Scan package.json for vulnerable packages."""
        fixes: list[CVEFix] = []
        pkg_json = self.worktree_path / "package.json"

        if not pkg_json.exists():
            return fixes

        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return fixes

        deps = {}
        deps.update(data.get("dependencies", {}))
        deps.update(data.get("devDependencies", {}))

        for pkg_name, version in deps.items():
            if pkg_name.lower() in self.vuln_db:
                # Clean version string
                clean_version = re.sub(r"[^0-9\.]", "", version) or "unknown"
                fixes.extend(
                    self._create_fixes(pkg_name.lower(), clean_version, "package.json")
                )

        return fixes

    def _create_fixes(
        self,
        pkg_name: str,
        current_version: str,
        file_path: str,
    ) -> list[CVEFix]:
        """Create fix suggestions for a vulnerable package."""
        fixes: list[CVEFix] = []
        vulns = self.vuln_db.get(pkg_name, [])

        for vuln in vulns:
            # Only report if current version is affected
            affected = vuln.get("affected_versions", "")
            if affected and not self._version_affected(current_version, affected):
                continue

            self._fix_counter += 1
            fixes.append(CVEFix(
                fix_id=f"fix-{self._fix_counter:04d}",
                cve_id=vuln["cve_id"],
                package_name=pkg_name,
                current_version=current_version,
                fixed_version=vuln["fixed_version"],
                severity=vuln["severity"],
                cvss_score=vuln["cvss_score"],
                description=vuln["description"],
                fix_type="upgrade",
                file_path=file_path,
                remediation_steps=[
                    f"Upgrade {pkg_name} from {current_version} to {vuln['fixed_version']}",
                    f"Run: pip install '{pkg_name}>={vuln['fixed_version']}'",
                    f"Verify the fix by running tests",
                    f"Review changelog for breaking changes",
                ],
                references=vuln.get("references", []),
            ))

        return fixes