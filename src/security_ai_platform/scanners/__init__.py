"""Secret Scanner — detects hardcoded secrets, API keys, tokens, and credentials.

Scans source code for patterns matching known secret formats (AWS keys, GitHub tokens,
Slack tokens, private keys, etc.) and reports them as findings.

Usage:
    scanner = SecretScanner(worktree_path="/path/to/repo")
    findings = scanner.scan()
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


class SecretSeverity(str, Enum):
    """Severity levels for secret findings."""
    CRITICAL = "critical"  # Private keys, cloud credentials
    HIGH = "high"         # API keys, tokens
    MEDIUM = "medium"     # Passwords, connection strings
    LOW = "low"           # Suspicious patterns


@dataclass
class SecretFinding:
    """A single secret finding."""
    finding_id: str
    secret_type: str
    severity: SecretSeverity
    file_path: str
    line_number: int
    line_content: str
    matched_pattern: str
    description: str
    remediation: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "secret_type": self.secret_type,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "matched_pattern": self.matched_pattern,
            "description": self.description,
            "remediation": self.remediation,
            "timestamp": self.timestamp,
        }


# Secret detection patterns
_SECRET_PATTERNS: list[dict[str, Any]] = [
    {
        "name": "AWS Access Key ID",
        "pattern": r"(?:AKIA|ASIA)[A-Z0-9]{16}",
        "severity": SecretSeverity.CRITICAL,
        "description": "AWS Access Key ID detected",
        "remediation": "Remove the AWS access key from code. Use IAM roles or environment variables instead.",
    },
    {
        "name": "AWS Secret Access Key",
        "pattern": r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key[\"'\s]*[:=]\s*[\"'][A-Za-z0-9/+=]{40}[\"']",
        "severity": SecretSeverity.CRITICAL,
        "description": "AWS Secret Access Key detected",
        "remediation": "Remove the AWS secret key from code. Rotate the key immediately if exposed.",
    },
    {
        "name": "GitHub Personal Access Token",
        "pattern": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}",
        "severity": SecretSeverity.CRITICAL,
        "description": "GitHub Personal Access Token detected",
        "remediation": "Remove the token from code. Revoke and regenerate the token immediately.",
    },
    {
        "name": "GitHub Fine-Grained Token",
        "pattern": r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}",
        "severity": SecretSeverity.CRITICAL,
        "description": "GitHub Fine-Grained Personal Access Token detected",
        "remediation": "Remove the token from code. Revoke and regenerate the token immediately.",
    },
    {
        "name": "Slack Token",
        "pattern": r"xox[abprs]-[A-Za-z0-9\-]{10,}",
        "severity": SecretSeverity.HIGH,
        "description": "Slack API token detected",
        "remediation": "Remove the Slack token from code. Regenerate the token immediately.",
    },
    {
        "name": "Slack Webhook URL",
        "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
        "severity": SecretSeverity.HIGH,
        "description": "Slack Webhook URL detected",
        "remediation": "Remove the webhook URL from code. Regenerate the webhook immediately.",
    },
    {
        "name": "Google API Key",
        "pattern": r"AIza[ A-Za-z0-9_\-]{35}",
        "severity": SecretSeverity.HIGH,
        "description": "Google API Key detected",
        "remediation": "Remove the API key from code. Restrict the key using API console.",
    },
    {
        "name": "Google Service Account Key",
        "pattern": r"(?i)\"type\":\s*\"service_account\"",
        "severity": SecretSeverity.CRITICAL,
        "description": "Google Service Account credentials detected",
        "remediation": "Remove the service account JSON from code. Use workload identity instead.",
    },
    {
        "name": "Private Key (RSA/DSA/EC/OpenSSH)",
        "pattern": r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
        "severity": SecretSeverity.CRITICAL,
        "description": "Private key detected in source code",
        "remediation": "Remove the private key from code immediately. Use a secrets manager.",
    },
    {
        "name": "JWT Token",
        "pattern": r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
        "severity": SecretSeverity.HIGH,
        "description": "JWT token detected",
        "remediation": "Remove the JWT token from code. The token may need to be invalidated.",
    },
    {
        "name": "Connection String (password)",
        "pattern": r"(?i)(?:mongodb|postgres|mysql|redis|amqp):\/\/[^:\s]+:[^@\s]+@[^/\s]+",
        "severity": SecretSeverity.HIGH,
        "description": "Connection string with embedded password detected",
        "remediation": "Remove the connection string from code. Use environment variables or a secrets manager.",
    },
    {
        "name": "Generic Password Assignment",
        "pattern": r"(?i)(?:password|passwd|pwd)[\"'\s]*[:=]\s*[\"'][^\"']{8,}[\"']",
        "severity": SecretSeverity.MEDIUM,
        "description": "Hardcoded password detected",
        "remediation": "Remove the hardcoded password. Use environment variables or a secrets manager.",
    },
    {
        "name": "Generic Secret Assignment",
        "pattern": r"(?i)(?:secret|api_key|apikey|token|auth)[\"'\s]*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']",
        "severity": SecretSeverity.MEDIUM,
        "description": "Hardcoded secret or API key detected",
        "remediation": "Remove the hardcoded secret. Use environment variables or a secrets manager.",
    },
    {
        "name": "NPM Token",
        "pattern": r"npm_[A-Za-z0-9]{36}",
        "severity": SecretSeverity.HIGH,
        "description": "NPM access token detected",
        "remediation": "Remove the NPM token from code. Revoke and regenerate the token.",
    },
    {
        "name": "Docker Hub Token",
        "pattern": r"dckr_pat_[A-Za-z0-9]{27,}",
        "severity": SecretSeverity.HIGH,
        "description": "Docker Hub personal access token detected",
        "remediation": "Remove the Docker token from code. Revoke and regenerate the token.",
    },
    {
        "name": "Stripe API Key",
        "pattern": r"(?:sk|pk)_(?:test|live)_[A-Za-z0-9]{24,}",
        "severity": SecretSeverity.CRITICAL,
        "description": "Stripe API key detected",
        "remediation": "Remove the Stripe key from code. Rotate the key immediately.",
    },
    {
        "name": "Twilio API Key",
        "pattern": r"SK[A-Za-z0-9]{32}",
        "severity": SecretSeverity.HIGH,
        "description": "Twilio API key detected",
        "remediation": "Remove the Twilio key from code. Rotate the key immediately.",
    },
    {
        "name": "Azure Storage Connection String",
        "pattern": r"DefaultEndpointsProtocol=https;AccountName=[a-z0-9]+;AccountKey=[A-Za-z0-9+/=]{88}",
        "severity": SecretSeverity.CRITICAL,
        "description": "Azure Storage connection string with key detected",
        "remediation": "Remove the connection string from code. Use managed identity instead.",
    },
    {
        "name": "Azure Service Principal Secret",
        "pattern": r"(?i)(?:azure|azurerm)[_\-]?client[_\-]?secret[\"'\s]*[:=]\s*[\"'][A-Za-z0-9_\-]{32,}[\"']",
        "severity": SecretSeverity.CRITICAL,
        "description": "Azure service principal secret detected",
        "remediation": "Remove the secret from code. Use managed identity instead.",
    },
    {
        "name": "SSH Public Key (suspicious in code)",
        "pattern": r"ssh-(?:rsa|dsa|ed25519|ecdsa) [A-Za-z0-9+/=]{100,}",
        "severity": SecretSeverity.LOW,
        "description": "SSH public key found in source code",
        "remediation": "Review if the SSH key should be in source code. Consider removing it.",
    },
]

# Files to skip during scanning
_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "dist", "build", ".eggs", ".tox", ".idea",
    ".vscode", ".next", ".nuxt", "coverage", "htmlcov", ".terraform",
}

_SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dll", ".exe", ".bin", ".jpg", ".jpeg", ".png",
    ".gif", ".bmp", ".ico", ".svg", ".woff", ".woff2", ".ttf", ".eot",
    ".mp3", ".mp4", ".avi", ".mov", ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}

# Files that commonly contain false positives
_FALSE_POSITIVE_FILES = {
    "test_secret", "mock_secret", "fake_secret", "example_secret",
    "dummy_secret", "sample_secret", "test_key", "mock_key",
}


class SecretScanner:
    """Scans source code for hardcoded secrets and credentials.

    Uses regex patterns to detect common secret formats including cloud provider
    keys, API tokens, private keys, and database connection strings.

    Example:
        scanner = SecretScanner(worktree_path="/path/to/repo")
        findings = scanner.scan()
        for finding in findings:
            print(finding.secret_type, finding.file_path, finding.line_number)
    """

    def __init__(
        self,
        worktree_path: str = ".",
        custom_patterns: list[dict[str, Any]] | None = None,
        max_file_size_mb: float = 5.0,
    ) -> None:
        self.worktree_path = Path(worktree_path).resolve()
        self.patterns = _SECRET_PATTERNS + (custom_patterns or [])
        self.max_file_size = int(max_file_size_mb * 1024 * 1024)
        self._finding_counter = 0

    def scan(self) -> list[SecretFinding]:
        """Scan the worktree for secrets.

        Returns:
            List of SecretFinding objects for all detected secrets.
        """
        findings: list[SecretFinding] = []
        self._finding_counter = 0

        for file_path in self._iter_files():
            try:
                file_findings = self._scan_file(file_path)
                findings.extend(file_findings)
            except Exception as exc:
                logger.debug("Failed to scan %s: %s", file_path, exc)

        logger.info("Secret scan complete: %d findings in %s", len(findings), self.worktree_path)
        return findings

    def _iter_files(self):
        """Iterate over scannable files in the worktree."""
        try:
            for path in self.worktree_path.rglob("*"):
                if not path.is_file():
                    continue
                if self._should_skip(path):
                    continue
                if path.stat().st_size > self.max_file_size:
                    continue
                yield path
        except OSError as exc:
            logger.warning("Error iterating files: %s", exc)

    def _should_skip(self, path: Path) -> bool:
        """Determine if a file should be skipped."""
        # Skip by directory
        try:
            parts = path.relative_to(self.worktree_path).parts
        except ValueError:
            return True

        for part in parts[:-1]:
            if part in _SKIP_DIRS:
                return True

        # Skip by extension
        if path.suffix.lower() in _SKIP_EXTENSIONS:
            return True

        # Skip lock files
        if path.name in ("package-lock.json", "yarn.lock", "poetry.lock", "uv.lock"):
            return True

        # Skip false positive test files
        name_lower = path.name.lower()
        for fp in _FALSE_POSITIVE_FILES:
            if fp in name_lower:
                return True

        return False

    def _scan_file(self, file_path: Path) -> list[SecretFinding]:
        """Scan a single file for secrets."""
        findings: list[SecretFinding] = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            return findings

        lines = content.splitlines()
        rel_path = str(file_path.relative_to(self.worktree_path))

        for line_num, line in enumerate(lines, 1):
            # Skip comments (basic heuristic)
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern_def in self.patterns:
                pattern = pattern_def["pattern"]
                for match in re.finditer(pattern, line):
                    self._finding_counter += 1
                    findings.append(SecretFinding(
                        finding_id=f"secret-{self._finding_counter:04d}",
                        secret_type=pattern_def["name"],
                        severity=pattern_def["severity"],
                        file_path=rel_path,
                        line_number=line_num,
                        line_content=line.strip()[:200],
                        matched_pattern=match.group(0)[:50],
                        description=pattern_def["description"],
                        remediation=pattern_def["remediation"],
                    ))

        return findings