# InfraScan — Infrastructure as Code Security & Cost Scanner CLI

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive tool for scanning Terraform, CloudFormation, and Pulumi infrastructure-as-code files for security vulnerabilities, compliance violations, and cost optimization opportunities.

## Features

- **Multi-Cloud Support**: Scan Terraform (.tf), CloudFormation (YAML/JSON), and Pulumi configurations
- **Security Scanning**: 10+ built-in security rules covering IAM, networking, encryption, and access control
- **Compliance Checks**: Enforce tagging policies, naming conventions, and governance rules
- **Cost Estimation**: Estimate monthly AWS costs and find optimization opportunities
- **Multiple Output Formats**: JSON, HTML, and Markdown reports
- **CI/CD Integration**: Built-in plugins for GitHub Actions, GitLab CI, Jenkins, and Azure Pipelines
- **Extensible Rule Engine**: Write custom rules in YAML for your organization's policies
- **Fast & Lightweight**: Written in pure Python with minimal dependencies

## Installation

```bash
pip install infrascan
```

### Development Installation

```bash
git clone https://github.com/itsPremkumar/infrascan.git
cd infrascan
pip install -e ".[dev]"
```

## Quick Start

```bash
# Scan a directory of Terraform files
infrascan scan ./infrastructure

# Scan a specific file
infrascan scan main.tf

# Generate HTML report
infrascan scan ./infrastructure --format html --output report.html

# Only scan for security issues
infrascan scan ./infrastructure --category security

# Fail pipeline on medium or higher
infrascan scan ./infrastructure --fail-on medium

# Estimate costs
infrascan cost ./infrastructure

# List all available rules
infrascan list-rules

# Generate CI/CD pipeline config
infrascan init-cicd .github/workflows/infrascan.yml --format github
```

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan IaC files for security, compliance, and cost issues |
| `cost` | Estimate monthly cloud infrastructure costs |
| `parse` | Parse and display all resources found in IaC files |
| `list-rules` | List all available security/compliance/cost rules |
| `init-cicd` | Generate CI/CD pipeline configuration |

## Rules

### Security Rules (SEC001-SEC010)

| ID | Title | Severity |
|----|-------|----------|
| SEC001 | S3 Bucket Public Access Enabled | CRITICAL |
| SEC002 | S3 Bucket Public Read-Write Access | CRITICAL |
| SEC003 | Security Group Allows All Inbound Traffic | HIGH |
| SEC004 | Unencrypted EBS Volume | HIGH |
| SEC005 | IAM Policy with Full Admin Access | CRITICAL |
| SEC006 | RDS Instance Publicly Accessible | HIGH |
| SEC007 | Unencrypted SQS Queue | MEDIUM |
| SEC008 | S3 Bucket Versioning Disabled | MEDIUM |
| SEC009 | CloudTrail Logging Disabled | HIGH |
| SEC010 | Weak SSL/TLS Policy | MEDIUM |

### Compliance Rules (COMP001-COMP004)

| ID | Title | Severity |
|----|-------|----------|
| COMP001 | Missing Required Tags - Environment | MEDIUM |
| COMP002 | Missing Required Tags - Owner | LOW |
| COMP003 | Missing Cost Center Tag | LOW |
| COMP004 | Resource Naming Convention Violation | LOW |

### Cost Rules (COST001-COST005)

| ID | Title | Severity |
|----|-------|----------|
| COST001 | Oversized EC2 Instance | MEDIUM |
| COST002 | RDS Multi-AZ in Non-Production | LOW |
| COST003 | Unattached EBS Volume | LOW |
| COST004 | NAT Gateway in Development | MEDIUM |
| COST005 | S3 Intelligent Tiering Not Enabled | LOW |

## Custom Rules

Create a YAML file with your custom policies:

```yaml
rules:
  - id: CUSTOM001
    type: property
    title: S3 Bucket Must Have Logging
    description: S3 buckets should have access logging enabled
    severity: medium
    resource_types:
      - aws_s3_bucket
    property_name: logging
    required: true
    remediation: "Add a logging block to the S3 bucket"
    category: compliance

  - id: CUSTOM002
    type: tag
    title: Required Data Classification Tag
    severity: high
    required_tags:
      - DataClassification
    remediation: "Add DataClassification tag"
    category: compliance
```

Load custom rules during scan:

```bash
infrascan scan ./infrastructure --rules custom-rules.yaml
```

### Rule Types

- **property**: Checks resource properties for expected/forbidden values or required presence
- **tag**: Checks for required tags on resources

### Rule Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique rule identifier |
| `type` | Yes | Rule type: `property` or `tag` |
| `title` | Yes | Short rule title |
| `description` | Yes | Rule description |
| `severity` | No | `critical`, `high`, `medium`, `low`, `info` (default: medium) |
| `resource_types` | Yes (property) | List of resource type patterns to match |
| `property_name` | Yes (property) | Property to check |
| `expected_value` | No | Property must equal this value |
| `forbidden_value` | No | Property must NOT equal this value |
| `required` | No | Property must be present (default: false) |
| `required_tags` | Yes (tag) | List of required tag keys |
| `remediation` | No | How to fix the issue |
| `category` | No | `security`, `compliance`, or `cost` |

## CI/CD Integration

### GitHub Actions

```yaml
name: InfraScan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install infrascan
      - run: infrascan scan ./infrastructure --format html --output report.html --fail-on high
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: infrascan-report
          path: report.html
```

### GitLab CI

```yaml
infrascan:
  image: python:3.11
  stage: test
  script:
    - pip install infrascan
    - infrascan scan ./infrastructure --format json --output report.json --fail-on high
  artifacts:
    when: always
    paths:
      - report.json
```

### Jenkins

```groovy
stage('InfraScan') {
    steps {
        sh 'pip install infrascan'
        sh 'infrascan scan ./infrastructure --format html --output report.html --fail-on high'
        publishHTML(target: [
            reportDir: '.', reportFiles: 'report.html', reportName: 'InfraScan'
        ])
    }
}
```

## Output Formats

### JSON
Structured JSON output suitable for automation and downstream tooling.

### HTML
Interactive dashboard with severity cards, sortable findings table, and dark theme.

### Markdown
GitHub-friendly markdown with severity tables and detailed findings.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No findings above threshold |
| 1 | Findings detected at or above `--fail-on` threshold |

## Examples

See the `examples/` directory for:
- `main.tf` — Terraform with intentional issues
- `cloudformation.yaml` — CloudFormation with intentional issues
- `custom-rules.yaml` — Example custom rules

## License

MIT
