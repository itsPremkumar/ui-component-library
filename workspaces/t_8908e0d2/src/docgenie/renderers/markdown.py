"""Markdown renderer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docgenie.core import OpenAPISpec


class MarkdownRenderer:
    """Render API documentation as Markdown."""

    def render(self, spec: OpenAPISpec, output_path: Path, theme: str = "default", **kwargs: Any) -> Path:
        """Generate Markdown documentation."""
        md = self._build_markdown(spec)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")
        return output_path

    def _build_markdown(self, spec: OpenAPISpec) -> str:
        """Build the complete Markdown document."""
        lines: list[str] = []
        lines.append(f"# {spec.title}")
        lines.append(f"**Version:** {spec.version}")
        lines.append(f"**Base URL:** {spec.base_url}")
        lines.append("")
        lines.append(f"{spec.description}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Table of Contents")
        lines.append("")
        grouped = spec.grouped_endpoints
        for tag in sorted(grouped.keys()):
            anchor = tag.lower().replace(" ", "-")
            lines.append(f"- [{tag}](#{anchor})")
        lines.append("- [Schemas](#schemas)")
        lines.append("")
        lines.append("---")
        lines.append("")

        for tag, endpoints in sorted(grouped.items()):
            anchor = tag.lower().replace(" ", "-")
            lines.append(f"## {tag}")
            lines.append("")
            for ep in endpoints:
                lines.append(f"### `{ep.method}` {ep.path}")
                lines.append("")
                if ep.deprecated:
                    lines.append("> **DEPRECATED**")
                    lines.append("")
                if ep.summary:
                    lines.append(f"**Summary:** {ep.summary}")
                    lines.append("")
                if ep.description:
                    lines.append(f"{ep.description}")
                    lines.append("")
                if ep.parameters:
                    lines.append("**Parameters:**")
                    lines.append("")
                    lines.append("| Name | In | Required | Type | Description |")
                    lines.append("|------|-----|----------|------|-------------|")
                    for p in ep.parameters:
                        name = p.get("name", "")
                        param_in = p.get("in", "")
                        required = "Yes" if p.get("required") else "No"
                        param_type = p.get("type", p.get("schema", {}).get("type", ""))
                        desc = p.get("description", "")
                        lines.append(f"| `{name}` | {param_in} | {required} | {param_type} | {desc} |")
                    lines.append("")

                if ep.responses:
                    lines.append("**Responses:**")
                    lines.append("")
                    for code, resp in ep.responses.items():
                        desc = resp.get("description", "")
                        lines.append(f"- `{code}` — {desc}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        if spec.schemas:
            lines.append("## Schemas")
            lines.append("")
            for name, schema in spec.schemas.items():
                lines.append(f"### {name}")
                lines.append("")
                lines.append("```json")
                lines.append(json.dumps(schema, indent=2))
                lines.append("```")
                lines.append("")

        return "\n".join(lines)
