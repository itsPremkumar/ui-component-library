"""CLI interface for DocGenie."""

from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from docgenie import DocGenerator, OpenAPIParser
from docgenie.renderers.html import HTMLRenderer
from docgenie.renderers.markdown import MarkdownRenderer
from docgenie.renderers.pdf import PDFRenderer
from docgenie.comparator.diff import SpecComparator
from docgenie.themes.manager import ThemeManager, ThemeConfig

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="docgenie")
def main():
    """DocGenie — Automated API Documentation Generator."""
    pass


@main.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", "formats", multiple=True, type=click.Choice(["html", "md", "pdf", "all"]),
              default=["html"], help="Output format(s)")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=Path("./docs"),
              help="Output directory")
@click.option("--theme", "-t", default="default", help="Theme name")
@click.option("--base-url", default="", help="Override base URL")
def generate(spec_file: Path, formats: tuple[str, ...], output: Path, theme: str, base_url: str):
    """Generate API documentation from an OpenAPI/Swagger spec."""
    with console.status("[bold green]Parsing spec..."):
        parser = OpenAPIParser()
        spec = parser.parse(spec_file)

    if base_url:
        spec.base_url = base_url

    generator = DocGenerator(spec, theme=theme)
    generator.register_renderer("html", HTMLRenderer())
    generator.register_renderer("md", MarkdownRenderer())
    generator.register_renderer("pdf", PDFRenderer())

    format_list = list(fmts for fmts in formats)
    if "all" in format_list:
        format_list = ["html", "md", "pdf"]

    with console.status("[bold green]Rendering documentation..."):
        results = generator.render_all(output, formats=format_list)

    console.print(f"\n[bold green]Documentation generated successfully![/bold green]")
    console.print(f"  Spec: [cyan]{spec.title} v{spec.version}[/cyan]")
    console.print(f"  Endpoints: [cyan]{len(spec.endpoints)}[/cyan]")
    console.print(f"  Theme: [cyan]{theme}[/cyan]\n")

    table = Table(title="Output Files")
    table.add_column("Format", style="cyan")
    table.add_column("Path", style="green")
    for fmt, path in results.items():
        table.add_row(fmt, str(path))
    console.print(table)


@main.command()
@click.argument("spec_a", type=click.Path(exists=True, path_type=Path))
@click.argument("spec_b", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "-f", "fmt", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
def compare(spec_a: Path, spec_b: Path, fmt: str):
    """Compare two API spec versions."""
    parser = OpenAPIParser()
    with console.status("[bold green]Parsing specs..."):
        parsed_a = parser.parse(spec_a)
        parsed_b = parser.parse(spec_b)

    comparator = SpecComparator()
    result = comparator.compare(parsed_a, parsed_b)

    if fmt == "json":
        output = {
            "spec_a": {"title": result.spec_a_title, "version": result.spec_a_version},
            "spec_b": {"title": result.spec_b_title, "version": result.spec_b_version},
            "total_changes": len(result.changes),
            "breaking_changes": len(result.breaking_changes),
            "backward_compatible": result.is_compatible,
            "changes": [
                {
                    "type": c.change_type.value,
                    "category": c.category,
                    "path": c.path,
                    "detail": c.detail,
                }
                for c in result.changes
            ],
        }
        console.print(json.dumps(output, indent=2))
    else:
        console.print(f"\n[bold cyan]API Version Comparison[/bold cyan]")
        console.print(result.summary())

        if result.changes:
            table = Table(title="Changes Detail")
            table.add_column("Type", style="cyan", width=12)
            table.add_column("Category", style="yellow", width=12)
            table.add_column("Path", style="green")
            table.add_column("Detail", style="white")
            for c in result.changes:
                color = {
                    "added": "green",
                    "removed": "red",
                    "modified": "yellow",
                    "deprecated": "magenta",
                }.get(c.change_type.value, "white")
                table.add_row(
                    f"[{color}]{c.change_type.value}[/{color}]",
                    c.category,
                    c.path,
                    c.detail,
                )
            console.print(table)


@main.command()
@click.option("--theme-dir", type=click.Path(path_type=Path), default=None,
              help="Custom theme directory")
def themes(theme_dir: str):
    """List available themes."""
    manager = ThemeManager(theme_dir=Path(theme_dir) if theme_dir else None)
    available = manager.list_themes()

    console.print(f"\n[bold cyan]Available Themes[/bold cyan]\n")
    table = Table()
    table.add_column("Theme", style="cyan")
    table.add_column("Type", style="yellow")
    for name in available:
        is_builtin = name in ThemeManager.BUILT_IN_THEMES
        table.add_row(name, "Built-in" if is_builtin else "Custom")
    console.print(table)


@main.command()
@click.argument("name")
@click.option("--primary-color", default="#2563eb", help="Primary color (hex)")
@click.option("--bg-color", default="#f8fafc", help="Background color (hex)")
@click.option("--text-color", default="#1e293b", help="Text color (hex)")
@click.option("--font", default="-apple-system, sans-serif", help="Font family")
@click.option("--brand", default="", help="Brand name")
@click.option("--footer", default="", help="Footer text")
@click.option("--theme-dir", type=click.Path(path_type=Path), default=None,
              help="Custom theme directory")
def create_theme(name: str, primary_color: str, bg_color: str, text_color: str,
                 font: str, brand: str, footer: str, theme_dir: str):
    """Create a custom theme."""
    config = ThemeConfig(
        name=name,
        primary_color=primary_color,
        background_color=bg_color,
        text_color=text_color,
        font_family=font,
        brand_name=brand,
        footer_text=footer,
    )
    manager = ThemeManager(theme_dir=Path(theme_dir) if theme_dir else None)
    path = manager.create_theme(name, config)
    console.print(f"[bold green]Theme created:[/bold green] {path}")


@main.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
def info(spec_file: Path):
    """Show spec information."""
    parser = OpenAPIParser()
    spec = parser.parse(spec_file)

    console.print(f"\n[bold cyan]API Specification Info[/bold cyan]\n")
    console.print(f"  Title: [green]{spec.title}[/green]")
    console.print(f"  Version: [green]{spec.version}[/green]")
    console.print(f"  Description: {spec.description}")
    console.print(f"  Base URL: [green]{spec.base_url}[/green]")
    console.print(f"  Endpoints: [green]{len(spec.endpoints)}[/green]")
    console.print(f"  Schemas: [green]{len(spec.schemas)}[/green]")
    console.print(f"  Servers: [green]{len(spec.servers)}[/green]")

    if spec.endpoints:
        table = Table(title="Endpoints")
        table.add_column("Method", style="cyan", width=8)
        table.add_column("Path", style="green")
        table.add_column("Summary", style="white")
        table.add_column("Deprecated", style="red", width=10)
        for ep in spec.endpoints:
            table.add_row(
                ep.method, ep.path, ep.summary[:60], "Yes" if ep.deprecated else ""
            )
        console.print(table)


if __name__ == "__main__":
    main()
