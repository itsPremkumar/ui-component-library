"""CI/CD integration plugins for automated scanning."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CICDResult:
    """Result from a CI/CD scan that can be consumed by pipelines."""
    exit_code: int
    passed: bool
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    fail_on: str
    output: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "exit_code": self.exit_code,
            "passed": self.passed,
            "findings_count": self.findings_count,
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
            "fail_on": self.fail_on,
        }


class CICDScanner:
    """Scans IaC files and produces CI/CD-friendly output."""

    def __init__(self, scanner: Any, fail_on: str = "high"):
        self.scanner = scanner
        self.fail_on = fail_on

    def _should_fail(self, result: Any) -> bool:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        threshold = severity_order.get(self.fail_on, 1)

        if threshold <= 0 and result.critical_count > 0:
            return True
        if threshold <= 1 and result.high_count > 0:
            return True
        if threshold <= 2 and result.medium_count > 0:
            return True
        if threshold <= 3 and result.low_count > 0:
            return True
        if threshold <= 4 and result.info_count > 0:
            return True
        return False

    def scan_and_report(
        self,
        target: str,
        output_format: str = "json",
        output_file: Optional[str] = None,
        rules_file: Optional[str] = None,
    ) -> CICDResult:
        """Run scan and produce CI/CD result."""
        import time
        from pathlib import Path

        from infrascan.reports import get_generator
        from infrascan.rules import RuleEngine
        from infrascan.cost import CostEstimator
        from infrascan.schemas import ScanResult

        start_time = time.time()

        from infrascan.parsers import ParserRegistry
        registry = ParserRegistry()
        target_path = Path(target)

        if target_path.is_file():
            resources = registry.parse_file(target_path)
            files_scanned = 1
        elif target_path.is_dir():
            resources = registry.scan_directory(target_path)
            files_scanned = len(set(r.source_file for r in resources))
        else:
            resources = []
            files_scanned = 0

        engine = RuleEngine()
        engine.load_builtin_rules()
        if rules_file:
            engine.load_custom_rules(Path(rules_file))
        findings = engine.scan(resources)

        estimator = CostEstimator()
        cost_findings = estimator.find_optimizations(resources)
        findings.extend(cost_findings)

        scan_time = time.time() - start_time

        result = ScanResult(
            findings=findings,
            resources_scanned=len(resources),
            files_scanned=files_scanned,
            scan_duration_seconds=scan_time,
        )

        if output_format in ("json", "html", "markdown"):
            generator = get_generator(output_format)
            content = generator.generate(result, Path(output_file) if output_file else None)
        else:
            content = f"Scan complete: {len(findings)} findings"

        passed = not self._should_fail(result)

        return CICDResult(
            exit_code=0 if passed else 1,
            passed=passed,
            findings_count=len(findings),
            critical_count=result.critical_count,
            high_count=result.high_count,
            medium_count=result.medium_count,
            low_count=result.low_count,
            fail_on=self.fail_on,
            output=content,
        )


def generate_github_action() -> str:
    """Generate GitHub Actions workflow for InfraScan."""
    return """name: InfraScan Security Scan
on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]

jobs:
  infrascan:
    name: Infrastructure Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install InfraScan
        run: pip install infrascan

      - name: Run InfraScan
        run: |
          infrascan scan ./infrastructure \\
            --format html \\
            --output infrascan-report.html \\
            --fail-on high

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: infrascan-report
          path: infrascan-report.html

      - name: Check Results
        run: |
          if [ $? -ne 0 ]; then
            echo "::error::InfraScan found critical/high severity issues"
            exit 1
          fi
"""


def generate_gitlab_ci() -> str:
    """Generate GitLab CI configuration for InfraScan."""
    return """infrascan:
  image: python:3.11
  stage: test
  script:
    - pip install infrascan
    - infrascan scan ./infrastructure --format json --output report.json --fail-on high
  artifacts:
    when: always
    paths:
      - report.json
    reports:
      junit: report.json
  allow_failure: false
"""


def generate_jenkinsfile() -> str:
    """Generate Jenkins pipeline for InfraScan."""
    return """pipeline {
    agent any
    stages {
        stage('InfraScan') {
            steps {
                sh 'pip install infrascan'
                sh 'infrascan scan ./infrastructure --format html --output report.html --fail-on high'
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'InfraScan Report'
                ])
            }
        }
    }
}
"""


def generate_azure_pipeline() -> str:
    """Generate Azure DevOps pipeline for InfraScan."""
    return """trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    pip install infrascan
    infrascan scan ./infrastructure --format json --output $(Build.ArtifactStagingDirectory)/report.json --fail-on high
  displayName: 'Run InfraScan'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'infrascan-report'
"""
