"""OpenAPI/Swagger specification parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from docgenie.core import APIEndpoint, OpenAPISpec


class OpenAPIParser:
    """Parse OpenAPI 2.0 (Swagger) and 3.0 specifications."""

    def parse(self, source: str | Path) -> OpenAPISpec:
        """Parse an OpenAPI spec from a file path or JSON/YAML string."""
        if isinstance(source, Path) or (
            isinstance(source, str) and Path(source).suffix in (".json", ".yaml", ".yml")
        ):
            path = Path(source)
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                data = json.loads(text)
            else:
                data = yaml.safe_load(text)
        else:
            # Try JSON first, then YAML
            try:
                data = json.loads(source)
            except json.JSONDecodeError:
                data = yaml.safe_load(source)

        return self._build_spec(data)

    def _build_spec(self, data: dict[str, Any]) -> OpenAPISpec:
        """Build an OpenAPISpec from parsed data."""
        spec = OpenAPISpec(raw=data)

        # Detect version
        if "openapi" in data:
            # OpenAPI 3.x
            spec.title = data.get("info", {}).get("title", "Untitled API")
            spec.version = data.get("info", {}).get("version", "0.0.0")
            spec.description = data.get("info", {}).get("description", "")
            spec.servers = data.get("servers", [])
            spec.tags = data.get("tags", [])
            spec.schemas = data.get("components", {}).get("schemas", {})
            spec.security_schemes = data.get("components", {}).get("securitySchemes", {})

            for server in spec.servers:
                if "url" in server:
                    spec.base_url = server["url"]
                    break

            paths = data.get("paths", {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method in ("parameters", "summary", "description", "servers"):
                        continue
                    spec.endpoints.append(self._parse_endpoint_3x(method, path, details))

        elif "swagger" in data:
            # Swagger 2.0
            spec.title = data.get("info", {}).get("title", "Untitled API")
            spec.version = data.get("info", {}).get("version", "0.0.0")
            spec.description = data.get("info", {}).get("description", "")
            spec.base_url = data.get("host", "")
            if data.get("basePath"):
                spec.base_url = f"{data.get('schemes', ['https'])[0]}://{spec.base_url}{data['basePath']}"
            spec.schemas = data.get("definitions", {})
            spec.security_schemes = data.get("securityDefinitions", {})

            paths = data.get("paths", {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method == "parameters":
                        continue
                    spec.endpoints.append(self._parse_endpoint_2x(method, path, details))

        return spec

    def _parse_endpoint_3x(self, method: str, path: str, details: dict[str, Any]) -> APIEndpoint:
        """Parse an OpenAPI 3.x endpoint."""
        return APIEndpoint(
            method=method.upper(),
            path=path,
            summary=details.get("summary", ""),
            description=details.get("description", ""),
            operation_id=details.get("operationId", ""),
            parameters=details.get("parameters", []),
            request_body=details.get("requestBody"),
            responses=details.get("responses", {}),
            tags=details.get("tags", []),
            deprecated=details.get("deprecated", False),
            security=details.get("security", []),
        )

    def _parse_endpoint_2x(self, method: str, path: str, details: dict[str, Any]) -> APIEndpoint:
        """Parse a Swagger 2.0 endpoint."""
        return APIEndpoint(
            method=method.upper(),
            path=path,
            summary=details.get("summary", ""),
            description=details.get("description", ""),
            operation_id=details.get("operationId", ""),
            parameters=details.get("parameters", []),
            responses=details.get("responses", {}),
            tags=details.get("tags", []),
            deprecated=details.get("deprecated", False),
            security=details.get("security", []),
        )
