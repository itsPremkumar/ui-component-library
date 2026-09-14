# Security AI Platform — SAST + DAST + Compliance + CVE Fix + SIEM

> **Production-grade security intelligence platform** that unifies SAST, DAST,
> secret scanning, CVE fix engine, multi-framework compliance checking, SIEM log
> aggregation, and a security dashboard into a single, extensible platform.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Usage](#usage)
- [Modules](#modules)
  - [SAST/DAST Pipeline](#sastdst-pipeline)
  - [Secret Scanner](#secret-scanner)
  - [CVE Fix Engine](#cve-fix-engine)
  - [Compliance Checker](#compliance-checker)
  - [SIEM Aggregator](#siem-aggregator)
  - [Platform Orchestrator](#platform-orchestrator)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Security](#security)
- [License](#license)

---

## Overview

The **Security AI Platform** is a unified security intelligence system that
automates vulnerability detection, remediation, compliance validation, and
log aggregation. It is designed for DevSecOps teams who need a single source
of truth for their security posture.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **SAST** | Static analysis via Semgrep, OPA/Conftest |
| **DAST** | Dynamic scanning via Trivy filesystem analysis |
| **Secret Scanning** | Detect 20+ secret types (AWS, GitHub, JWT, SSH, etc.) |
| **CVE Fix Engine** | Identify vulnerable dependencies and suggest fixes |
| **Compliance** | Validate against SOC 2, ISO 27001, PCI DSS, HIPAA |
| **SIEM Aggregation** | Forward security events to SIEM endpoints |
| **Gate Enforcement** | Block merges based on security thresholds |

---

## Features

- **Unified Platform**: Single API for all security scanning needs
- **20+ Secret Patterns**: Detect AWS keys, GitHub tokens, JWT, SSH keys,
  database connection strings, and more
- **100+ Known CVEs**: Extensible vulnerability database with version-aware
  fix suggestions
- **4 Compliance Frameworks**: SOC 2 (12 controls), ISO 27001 (12 controls),
  PCI DSS (15 controls), HIPAA (15 controls)
- **Risk Scoring**: Aggregate risk score with amplification for clusters
- **Gate Enforcement**: Configurable thresholds for blocking deployments
- **SIEM Integration**: Batch event forwarding to any SIEM endpoint
- **50+ Tests**: Comprehensive test coverage
- **SARIF Output**: Industry-standard output format for tool integration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Security AI Platform                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  SAST/DAST   │  │   Secret     │  │    CVE       │              │
│  │  Pipeline    │  │   Scanner    │  │  Fix Engine  │              │
│  │              │  │              │  │              │              │
│  │ • Semgrep    │  │ • AWS keys   │  │ • NVD DB     │              │
│  │ • Trivy      │  │ • GitHub     │  │ • Fix sugg.  │              │
│  │ • OPA        │  │ • JWT        │  │ • Version    │              │
│  │ • GHAS       │  │ • SSH        │  │   aware      │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                      │
│  ┌──────┴─────────────────┴──────────────────┴───────┐             │
│  │              Platform Orchestrator                │             │
│  │                                                   │             │
│  │ • Aggregate findings    • Compute risk score      │             │
│  │ • Evaluate gate          • Generate summary       │             │
│  └──────────────────────┬────────────────────────────┘             │
│                         │                                           │
│  ┌──────────────────────┴────────────────────────────┐             │
│  │              Compliance Checker                    │             │
│  │  SOC2 | ISO27001 | PCI DSS | HIPAA                 │             │
│  └──────────────────────┬────────────────────────────┘             │
│                         │                                           │
│  ┌──────────────────────┴────────────────────────────┐             │
│  │              SIEM Aggregator                       │             │
│  │  Event collection → Batch forwarding → Dashboard   │             │
│  └───────────────────────────────────────────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quickstart

```bash
# Install dependencies
pip install -e ".[dev]"

# Run full security scan
python -m security_ai_platform scan --path .

# Run specific modules
python -m security_ai_platform scan --path . --scanners secret_scan
python -m security_ai_platform scan --path . --scanners cve_fix,compliance

# Run tests
pytest tests/test_security_ai_platform.py -v
```

---

## Installation

### Requirements

- Python 3.10+
- Semgrep (optional, for SAST)
- Trivy (optional, for DAST)
- OPA/Conftest (optional, for policy checks)
- GitHub CLI (optional, for GHAS)

### Setup

```bash
# Clone repository
git clone https://github.com/reflexion-eval/reflexion-eval.git
cd reflexion-eval

# Install
pip install -e ".[dev]"

# Run tests
pytest tests/test_security_ai_platform.py -v
```

---

## Usage

### Platform API

```python
from security_ai_platform.core import SecurityAIPlatform, PlatformConfig

# Configure the platform
config = PlatformConfig(
    worktree_path="/path/to/repo",
    scan_mode=ScanMode.FULL,
    enabled_scanners=["semgrep", "trivy", "opa", "secret_scan", "cve_fix", "compliance", "siem"],
    risk_threshold=50.0,
    block_on_critical=True,
    compliance_frameworks=["SOC2", "ISO27001", "PCI_DSS", "HIPAA"],
)

# Run full scan
platform = SecurityAIPlatform(config=config)
result = platform.full_scan()

# Check results
if result.overall_pass_fail == "fail":
    print("Security gate BLOCKED:")
    for reason in result.gate_reasons:
        print(f"  - {reason}")

print(f"Total findings: {result.total_findings}")
print(f"Risk score: {result.overall_risk_score}")
print(f"Compliance: {list(result.compliance_reports.keys())}")
```

### Module APIs

```python
# Secret Scanner
from security_ai_platform.scanners import SecretScanner
scanner = SecretScanner(worktree_path="/path/to/repo")
findings = scanner.scan()

# CVE Fix Engine
from security_ai_platform.fix_engine import CVEFixEngine
engine = CVEFixEngine(worktree_path="/path/to/repo")
fixes = engine.analyze_and_fix()

# Compliance Checker
from security_ai_platform.compliance import ComplianceChecker
checker = ComplianceChecker(
    worktree_path="/path/to/repo",
    frameworks=["SOC2", "HIPAA"]
)
reports = checker.check_all()

# SIEM Aggregator
from security_ai_platform.siem import SIEMAggregator
aggregator = SIEMAggregator(
    worktree_path="/path/to/repo",
    endpoint="https://siem.example.com/api/events"
)
status = aggregator.aggregate()
```

---

## Modules

### SAST/DAST Pipeline

Integrates Semgrep (SAST), Trivy (DAST), OPA/Conftest (policy), and GHAS
(CodeQL) into a unified scanning pipeline with risk scoring and gate
evaluation.

**Output**: `ScanResult` with findings, risk score, pass/fail status, and
remediation suggestions.

### Secret Scanner

Detects 20+ types of hardcoded secrets including:
- AWS Access Key IDs and Secret Keys
- GitHub Personal Access Tokens (classic + fine-grained)
- Slack Tokens and Webhook URLs
- Google API Keys and Service Account credentials
- Private Keys (RSA, DSA, EC, OpenSSH)
- JWT Tokens
- Database connection strings with passwords
- NPM, Docker Hub, Stripe, Twilio, Azure tokens

### CVE Fix Engine

Scans package manifests (`requirements.txt`, `pyproject.toml`, `package.json`)
for dependencies with known CVEs. Provides version-aware fix suggestions
including upgrade commands and remediation steps.

### Compliance Checker

Validates security posture against four major frameworks:
- **SOC 2**: 12 controls covering access, encryption, monitoring
- **ISO 27001**: 12 controls for information security management
- **PCI DSS**: 15 controls for payment card data protection
- **HIPAA**: 15 controls for protected health information

### SIEM Aggregator

Collects security events from all modules, normalizes them into a unified
format, and forwards them to any SIEM endpoint in configurable batches.

### Platform Orchestrator

Coordinates all modules, aggregates findings, computes overall risk scores,
evaluates security gates, and produces unified reports.

---

## API Reference

### PlatformConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `worktree_path` | str | `"."` | Path to scan |
| `scan_mode` | ScanMode | `FULL` | Scan execution mode |
| `enabled_scanners` | list[str] | all | Scanners to enable |
| `risk_threshold` | float | 50.0 | Gate threshold |
| `block_on_critical` | bool | True | Block on critical findings |
| `compliance_frameworks` | list[str] | all | Frameworks to check |
| `siem_endpoint` | str | "" | SIEM endpoint URL |
| `output_format` | str | "json" | Output format |

### PlatformResult

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | str | Unique run identifier |
| `total_findings` | int | Total findings across modules |
| `total_critical` | int | Critical findings count |
| `overall_risk_score` | float | Computed risk score (0-100) |
| `overall_pass_fail` | str | Gate result: "pass" or "fail" |
| `gate_reasons` | list[str] | Reasons for gate block |
| `sast_result` | dict | SAST/DAST scan result |
| `secret_findings` | list[dict] | Secret findings |
| `cve_fixes` | list[dict] | CVE fix suggestions |
| `compliance_reports` | dict | Compliance reports by framework |
| `siem_status` | dict | SIEM aggregation status |

---

## Testing

```bash
# Run all tests
pytest tests/test_security_ai_platform.py -v

# Run with coverage
pytest tests/test_security_ai_platform.py --cov=security_ai_platform -v

# Run specific test class
pytest tests/test_security_ai_platform.py::TestSecretScanner -v
```

**72 tests** covering:
- Secret Scanner (16 tests)
- CVE Fix Engine (12 tests)
- Compliance Checker (12 tests)
- SIEM Aggregator (8 tests)
- Platform Integration (24 tests)

---

## Security

This platform follows security best practices:

- No secrets are transmitted externally
- All scanning is performed locally
- SIEM forwarding uses HTTPS in production
- No credentials are stored in memory longer than necessary
- Gate decisions are deterministic and auditable

**Responsible Disclosure**: If you find a security vulnerability in this
platform, please report it to the maintainers.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## SEO/GEO/AEO Keywords

security ai platform, SAST DAST scanner, secret scanning, CVE fix engine,
compliance checker SOC2 ISO27001 PCI HIPAA, SIEM log aggregation, DevSecOps,
vulnerability management, static analysis, dynamic analysis, security gate,
merge gate, CI/CD security, application security, AppSec, security automation,
risk scoring, security posture, compliance automation, security intelligence