"""Core data models and main generator class."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class APIEndpoint:
    """Represents a single API endpoint."""
    method: str
    path: str
    summary: str = ""
    description: str = ""
    operation_id: str = ""
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body: dict[str, Any] | None = None
    responses: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    deprecated: bool = False
    security: list[dict[str, list[str]]] = field(default_factory=list)


@dataclass
class OpenAPISpec:
    """Parsed OpenAPI specification."""
    title: str = ""
    version: str = ""
    description: str = ""
    base_url: str = ""
    endpoints: list[APIEndpoint] = field(default_factory=list)
    schemas: dict[str, Any] = field(default_factory=dict)
    security_schemes: dict[str, Any] = field(default_factory=dict)
    servers: list[dict[str, str]] = field(default_factory=list)
    tags: list[dict[str, str]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def grouped_endpoints(self) -> dict[str, list[APIEndpoint]]:
        """Group endpoints by tag."""
        groups: dict[str, list[APIEndpoint]] = {}
        for ep in self.endpoints:
            tag = ep.tags[0] if ep.tags else "default"
            groups.setdefault(tag, []).append(ep)
        return groups


class DocGenerator:
    """Main documentation generator orchestrator."""

    def __init__(self, spec: OpenAPISpec, theme: str = "default"):
        self.spec = spec
        self.theme = theme
        self._renderers: dict[str, Any] = {}

    def register_renderer(self, name: str, renderer: Any) -> None:
        """Register an output renderer."""
        self._renderers[name] = renderer

    def render(self, format: str, output_path: Path, **kwargs: Any) -> Path:
        """Render documentation to the specified format."""
        if format not in self._renderers:
            raise ValueError(
                f"Unknown format '{format}'. "
                f"Available: {list(self._renderers.keys())}"
            )
        renderer = self._renderers[format]
        return renderer.render(self.spec, output_path, theme=self.theme, **kwargs)

    def render_all(self, output_dir: Path, formats: list[str] | None = None, **kwargs: Any) -> dict[str, Path]:
        """Render to multiple formats at once."""
        output_dir.mkdir(parents=True, exist_ok=True)
        results: dict[str, Path] = {}
        fmts = formats or list(self._renderers.keys())
        for fmt in fmts:
            out = output_dir / f"api-docs.{fmt}"
            results[fmt] = self.render(fmt, out, **kwargs)
        return results
