"""Report generators for JSON, HTML, and Markdown output."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from infrascan.schemas import ScanResult, Severity


class ReportGenerator:
    """Base class for report generators."""

    def generate(self, result: ScanResult, output_path: Optional[Path] = None) -> str:
        """Generate a report. Returns the report content."""
        ...

    def _get_summary(self, result: ScanResult) -> dict[str, Any]:
        return {
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "total_findings": len(result.findings),
            "severity_breakdown": {
                "critical": result.critical_count,
                "high": result.high_count,
                "medium": result.medium_count,
                "low": result.low_count,
                "info": result.info_count,
            },
            "category_breakdown": {
                "security": len(result.by_category("security")),
                "compliance": len(result.by_category("compliance")),
                "cost": len(result.by_category("cost")),
            },
            "resources_scanned": result.resources_scanned,
            "files_scanned": result.files_scanned,
        }


class JsonReportGenerator(ReportGenerator):
    """Generate JSON reports."""

    def generate(self, result: ScanResult, output_path: Optional[Path] = None) -> str:
        report = {
            "infrascan_version": "1.0.0",
            "summary": self._get_summary(result),
            "findings": [f.to_dict() for f in result.findings],
        }
        content = json.dumps(report, indent=2, default=str)
        if output_path:
            output_path.write_text(content, encoding="utf-8")
        return content


class MarkdownReportGenerator(ReportGenerator):
    """Generate Markdown reports."""

    def generate(self, result: ScanResult, output_path: Optional[Path] = None) -> str:
        summary = self._get_summary(result)
        lines = [
            "# InfraScan Report",
            "",
            f"**Scan Date:** {summary['scan_time']}",
            f"**Files Scanned:** {summary['files_scanned']}",
            f"**Resources Scanned:** {summary['resources_scanned']}",
            "",
            "## Summary",
            "",
            "| Severity | Count |",
            "|----------|-------|",
            f"| CRITICAL | {summary['severity_breakdown']['critical']} |",
            f"| HIGH | {summary['severity_breakdown']['high']} |",
            f"| MEDIUM | {summary['severity_breakdown']['medium']} |",
            f"| LOW | {summary['severity_breakdown']['low']} |",
            f"| INFO | {summary['severity_breakdown']['info']} |",
            "",
            f"**Total Findings:** {summary['total_findings']}",
            "",
            "## Findings",
            "",
        ]

        for severity in Severity:
            sev_findings = [f for f in result.findings if f.severity == severity]
            if sev_findings:
                lines.append(f"### {severity.value.upper()} ({len(sev_findings)})")
                lines.append("")
                for f in sev_findings:
                    lines.append(f"#### {f.rule_id}: {f.title}")
                    lines.append(f"- **File:** `{f.file_path}:{f.line_number}`")
                    lines.append(f"- **Resource:** `{f.resource.resource_type}.{f.resource.name}`" if f.resource else "")
                    lines.append(f"- **Category:** {f.category}")
                    lines.append(f"- **Description:** {f.description}")
                    if f.remediation:
                        lines.append(f"- **Remediation:** {f.remediation}")
                    if f.references:
                        lines.append(f"- **References:** {', '.join(f.references)}")
                    lines.append("")

        content = "\n".join(lines)
        if output_path:
            output_path.write_text(content, encoding="utf-8")
        return content


class HtmlReportGenerator(ReportGenerator):
    """Generate HTML reports."""

    def generate(self, result: ScanResult, output_path: Optional[Path] = None) -> str:
        summary = self._get_summary(result)

        findings_html = ""
        for f in result.findings:
            findings_html += f"""
            <tr class="finding">
                <td>{f.rule_id}</td>
                <td>{f.title}</td>
                <td><span class="badge {f.severity.value}">{f.severity.value.upper()}</span></td>
                <td>{f.category}</td>
                <td><code>{f.file_path}:{f.line_number}</code></td>
                <td>{f.description[:80]}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>InfraScan Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }}
        h1 {{ color: #58a6ff; }}
        .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin: 2rem 0; }}
        .card {{ background: #161b22; border: 1px solid #21262d; border-radius: 6px; padding: 1rem; text-align: center; }}
        .card .number {{ font-size: 2rem; font-weight: bold; }}
        .card .label {{ color: #8b949e; }}
        .critical {{ color: #f85149; }}
        .high {{ color: #d29922; }}
        .medium {{ color: #db6d28; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #21262d; }}
        th {{ background: #161b22; color: #8b949e; }}
        .badge {{ padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge.critical {{ background: #f8514920; color: #f85149; }}
        .badge.high {{ background: #d2992220; color: #d29922; }}
        .badge.medium {{ background: #db6d2820; color: #db6d28; }}
    </style>
</head>
<body>
    <h1>InfraScan Security Report</h1>
    <div class="grid">
        <div class="card"><div class="number critical">{summary['severity_breakdown']['critical']}</div><div class="label">CRITICAL</div></div>
        <div class="card"><div class="number high">{summary['severity_breakdown']['high']}</div><div class="label">HIGH</div></div>
        <div class="card"><div class="number medium">{summary['severity_breakdown']['medium']}</div><div class="label">MEDIUM</div></div>
        <div class="card"><div class="number" style="color:#8b949e">{summary['severity_breakdown']['low']}</div><div class="label">LOW</div></div>
        <div class="card"><div class="number" style="color:#58a6ff">{summary['severity_breakdown']['info']}</div><div class="label">INFO</div></div>
    </div>
    <h2>Findings ({summary['total_findings']})</h2>
    <table>
        <thead><tr><th>Rule</th><th>Title</th><th>Severity</th><th>Category</th><th>Location</th><th>Description</th></tr></thead>
        <tbody>
            {findings_html if findings_html else '<tr><td colspan="6" style="text-align:center;color:#8b949e;">No findings</td></tr>'}
        </tbody>
    </table>
</body>
</html>"""

        if output_path:
            output_path.write_text(html, encoding="utf-8")
        return html


def get_generator(format_name: str) -> ReportGenerator:
    """Get a report generator by format name."""
    generators = {
        "json": JsonReportGenerator,
        "markdown": MarkdownReportGenerator,
        "html": HtmlReportGenerator,
    }
    gen_class = generators.get(format_name.lower())
    if gen_class is None:
        raise ValueError(f"Unknown format: {format_name}. Choose from: {', '.join(generators.keys())}")
    return gen_class()
