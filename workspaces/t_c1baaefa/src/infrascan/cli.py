"""InfraScan CLI - Main entry point."""

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from infrascan import __version__
from infrascan.schemas import Severity
from infrascan.parsers import ParserRegistry
from infrascan.rules import RuleEngine
from infrascan.cost import CostEstimator
from infrascan.schemas import ScanResult
from infrascan.reports import get_generator
from infrascan.cicd import CICDScanner, generate_github_action, generate_gitlab_ci, generate_jenkinsfile, generate_azure_pipeline

console = Console()


def _run_scan(
    target: Path,
    categories: list[str],
    fail_on: str,
    rules_file: Optional[Path] = None,
) -> ScanResult:
    """Run the full scan pipeline."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Parse
        task = progress.add_task("Parsing IaC files...", total=None)
        registry = ParserRegistry()
        if target.is_file():
            resources = registry.parse_file(target)
            files_scanned = 1
        else:
            resources = registry.scan_directory(target)
            files_scanned = len(set(r.source_file for r in resources))
        progress.update(task, completed=True)

        # Rules
        task = progress.add_task("Running security rules...", total=None)
        engine = RuleEngine()
        engine.load_builtin_rules()
        if rules_file:
            engine.load_custom_rules(rules_file)
        findings = engine.scan(resources)
        progress.update(task, completed=True)

        # Cost
        task = progress.add_task("Analyzing costs...", total=None)
        estimator = CostEstimator()
        cost_findings = estimator.find_optimizations(resources)
        findings.extend(cost_findings)
        progress.update(task, completed=True)

        # Filter categories
        if categories:
            findings = [f for f in findings if f.category in categories]

    result = ScanResult(
        findings=findings,
        resources_scanned=len(resources),
        files_scanned=files_scanned,
        scan_duration_seconds=0,
    )
    return result


def _display_results(result: ScanResult) -> None:
    """Display scan results in a table."""
    summary = (
        f"[bold]Resources Scanned:[/bold] {result.resources_scanned}  |  "
        f"[bold]Files:[/bold] {result.files_scanned}  |  "
        f"[bold]Duration:[/bold] {result.scan_duration_seconds:.2f}s"
    )
    console.print(Panel(summary, title="InfraScan Summary", border_style="blue"))

    if not result.findings:
        console.print("[green]No findings! Your infrastructure looks clean.[/green]")
        return

    table = Table(title=f"Findings ({len(result.findings)})")
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Rule", width=10)
    table.add_column("Category", width=10)
    table.add_column("Resource", width=20)
    table.add_column("File", width=25)
    table.add_column("Title", width=40)

    severity_styles = {
        Severity.CRITICAL: "bold red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "white",
        Severity.INFO: "blue",
    }

    for f in sorted(result.findings, key=lambda f: list(Severity).index(f.severity)):
        style = severity_styles.get(f.severity, "white")
        table.add_row(
            f"[{style}]{f.severity.value.upper()}[/{style}]",
            f.rule_id,
            f.category,
            f"{f.resource.resource_type}.{f.resource.name}" if f.resource else "-",
            f"{Path(f.file_path).name}:{f.line_number}" if f.file_path else "-",
            f.title[:40],
        )

    console.print(table)

    # Severity breakdown
    console.print(f"\n[bold red]Critical:[/bold red] {result.critical_count}  "
                  f"[bold orange]High:[/bold orange] {result.high_count}  "
                  f"[bold yellow]Medium:[/bold yellow] {result.medium_count}  "
                  f"[bold white]Low:[/bold white] {result.low_count}  "
                  f"[bold blue]Info:[/bold blue] {result.info_count}")


@click.group()
@click.version_option(version=__version__, prog_name="infrascan")
def main():
    """InfraScan - Infrastructure as Code Security & Cost Scanner CLI.

    Scan Terraform, CloudFormation, and Pulumi files for security
    vulnerabilities, compliance violations, and cost optimizations.
    """


@main.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--format", "-f", "output_format", type=click.Choice(["json", "html", "markdown", "table"]),
              default="table", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--category", "-c", multiple=True, type=click.Choice(["security", "compliance", "cost"]),
              help="Categories to scan (can be repeated)")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low", "info"]),
              default="high", help="Severity threshold for non-zero exit")
@click.option("--rules", "-r", type=click.Path(exists=True), help="Custom rules YAML file")
def scan(target, output_format, output, category, fail_on, rules):
    """Scan an IaC file or directory for issues."""
    target_path = Path(target)
    start_time = time.time()

    result = _run_scan(target_path, list(category), fail_on, Path(rules) if rules else None)
    result.scan_duration_seconds = time.time() - start_time

    if output_format == "table":
        _display_results(result)
    else:
        generator = get_generator(output_format)
        content = generator.generate(result, Path(output) if output else None)
        if output:
            console.print(f"[green]Report saved to {output}[/green]")
        else:
            console.print(content)

    # Exit with appropriate code
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    threshold = severity_order.get(fail_on, 1)
    if threshold <= 0 and result.critical_count > 0:
        sys.exit(1)
    if threshold <= 1 and result.high_count > 0:
        sys.exit(1)
    if threshold <= 2 and result.medium_count > 0:
        sys.exit(1)


@main.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--rules", "-r", type=click.Path(exists=True), help="Custom rules YAML file")
def cost(target, output, rules):
    """Estimate monthly costs for infrastructure."""
    target_path = Path(target)
    registry = ParserRegistry()

    if target_path.is_file():
        resources = registry.parse_file(target_path)
    else:
        resources = registry.scan_directory(target_path)

    estimator = CostEstimator()
    estimates, total = estimator.estimate_total(resources)

    if not estimates:
        console.print("[yellow]No costable resources found[/yellow]")
        return

    table = Table(title="Monthly Cost Estimate")
    table.add_column("Resource", width=25)
    table.add_column("Type", width=25)
    table.add_column("Monthly Cost", justify="right", width=15)
    table.add_column("Confidence", width=10)
    table.add_column("Notes", width=40)

    for est in estimates:
        table.add_row(
            est.resource_name,
            est.resource_type,
            f"${est.monthly_cost_usd:,.2f}",
            est.confidence,
            est.notes,
        )

    console.print(table)
    console.print(f"\n[bold green]Total Monthly Estimate: ${total:,.2f}[/bold green]")

    if output:
        import json
        data = {
            "estimates": [e.to_dict() for e in estimates],
            "total_monthly_usd": round(total, 2),
        }
        Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"[green]Report saved to {output}[/green]")


@main.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def parse(target, output):
    """Parse and display resources found in IaC files."""
    target_path = Path(target)
    registry = ParserRegistry()

    if target_path.is_file():
        resources = registry.parse_file(target_path)
    else:
        resources = registry.scan_directory(target_path)

    if not resources:
        console.print("[yellow]No resources found[/yellow]")
        return

    table = Table(title=f"Resources Found ({len(resources)})")
    table.add_column("Name", width=25)
    table.add_column("Type", width=30)
    table.add_column("File", width=30)
    table.add_column("Line", justify="right", width=6)
    table.add_column("Properties", width=40)

    for r in resources:
        props_str = ", ".join(f"{k}={v}" for k, v in list(r.properties.items())[:3])
        if len(r.properties) > 3:
            props_str += "..."
        table.add_row(
            r.name,
            r.resource_type,
            Path(r.source_file).name,
            str(r.line_start),
            props_str,
        )

    console.print(table)

    if output:
        import json
        data = [
            {
                "name": r.name,
                "type": r.resource_type,
                "file": r.source_file,
                "line": r.line_start,
                "properties": r.properties,
            }
            for r in resources
        ]
        Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"[green]Output saved to {output}[/green]")


@main.command()
@click.argument("output", type=click.Path())
@click.option("--format", type=click.Choice(["github", "gitlab", "jenkins", "azure"]),
              required=True, help="CI/CD platform")
def init_cicd(output, format):
    """Generate CI/CD pipeline configuration for automated scanning."""
    generators = {
        "github": generate_github_action,
        "gitlab": generate_gitlab_ci,
        "jenkins": generate_jenkinsfile,
        "azure": generate_azure_pipeline,
    }
    content = generators[format]()
    Path(output).write_text(content, encoding="utf-8")
    console.print(f"[green]CI/CD config ({format}) written to {output}[/green]")


@main.command()
def list_rules():
    """List all available rules."""
    engine = RuleEngine()
    engine.load_builtin_rules()

    table = Table(title=f"Available Rules ({engine.rule_count})")
    table.add_column("ID", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=10)
    table.add_column("Title", width=40)

    # Access internal rules list
    for rule in engine._rules:
        sev_colors = {
            Severity.CRITICAL: "bold red",
            Severity.HIGH: "red",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "white",
            Severity.INFO: "blue",
        }
        style = sev_colors.get(rule.severity, "white")
        table.add_row(
            rule.rule_id,
            f"[{style}]{rule.severity.value}[/{style}]",
            rule.category,
            rule.title[:40],
        )

    console.print(table)


if __name__ == "__main__":
    main()
