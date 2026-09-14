"""Tests for DocGenie core functionality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docgenie.core import APIEndpoint, DocGenerator, OpenAPISpec
from docgenie.parsers.openapi import OpenAPIParser
from docgenie.renderers.html import HTMLRenderer
from docgenie.renderers.markdown import MarkdownRenderer
from docgenie.comparator.diff import ChangeType, SpecComparator
from docgenie.themes.manager import ThemeConfig, ThemeManager


# Sample OpenAPI 3.0 spec
SAMPLE_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Pet Store API",
        "version": "1.0.0",
        "description": "A sample API for a pet store",
    },
    "servers": [{"url": "https://api.petstore.example.com/v1"}],
    "tags": [{"name": "pets", "description": "Pet operations"}],
    "paths": {
        "/pets": {
            "get": {
                "operationId": "listPets",
                "summary": "List all pets",
                "description": "Returns a list of all pets in the store",
                "tags": ["pets"],
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "description": "Maximum number of pets to return",
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {"description": "A list of pets"},
                    "500": {"description": "Internal server error"},
                },
            },
            "post": {
                "operationId": "createPet",
                "summary": "Create a pet",
                "description": "Add a new pet to the store",
                "tags": ["pets"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Pet"}
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Pet created"},
                    "400": {"description": "Invalid input"},
                },
            },
        },
        "/pets/{petId}": {
            "get": {
                "operationId": "getPetById",
                "summary": "Get a pet by ID",
                "tags": ["pets"],
                "parameters": [
                    {
                        "name": "petId",
                        "in": "path",
                        "required": True,
                        "description": "The pet ID",
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {"description": "Pet found"},
                    "404": {"description": "Pet not found"},
                },
            },
            "delete": {
                "operationId": "deletePet",
                "summary": "Delete a pet",
                "tags": ["pets"],
                "deprecated": True,
                "parameters": [
                    {
                        "name": "petId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "204": {"description": "Pet deleted"},
                    "404": {"description": "Pet not found"},
                },
            },
        },
    },
    "components": {
        "schemas": {
            "Pet": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "tag": {"type": "string"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer"},
                    "message": {"type": "string"},
                },
            },
        }
    },
}


@pytest.fixture
def sample_spec() -> OpenAPISpec:
    """Create a parsed sample spec."""
    parser = OpenAPIParser()
    return parser.parse(json.dumps(SAMPLE_SPEC))


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    return tmp_path / "docs"


class TestOpenAPIParser:
    """Tests for OpenAPIParser."""

    def test_parse_json_string(self):
        parser = OpenAPIParser()
        spec = parser.parse(json.dumps(SAMPLE_SPEC))
        assert spec.title == "Pet Store API"
        assert spec.version == "1.0.0"
        assert spec.base_url == "https://api.petstore.example.com/v1"
        assert len(spec.endpoints) == 4

    def test_parse_yaml_string(self):
        import yaml
        parser = OpenAPIParser()
        spec = parser.parse(yaml.dump(SAMPLE_SPEC))
        assert spec.title == "Pet Store API"
        assert len(spec.endpoints) == 4

    def test_parse_file(self, tmp_path: Path):
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(SAMPLE_SPEC))
        parser = OpenAPIParser()
        spec = parser.parse(spec_file)
        assert spec.title == "Pet Store API"

    def test_endpoints_parsed(self, sample_spec: OpenAPISpec):
        assert len(sample_spec.endpoints) == 4
        methods = [(e.method, e.path) for e in sample_spec.endpoints]
        assert ("GET", "/pets") in methods
        assert ("POST", "/pets") in methods
        assert ("GET", "/pets/{petId}") in methods
        assert ("DELETE", "/pets/{petId}") in methods

    def test_schemas_parsed(self, sample_spec: OpenAPISpec):
        assert "Pet" in sample_spec.schemas
        assert "Error" in sample_spec.schemas

    def test_deprecated_endpoint(self, sample_spec: OpenAPISpec):
        delete_ep = next(
            e for e in sample_spec.endpoints
            if e.method == "DELETE" and e.path == "/pets/{petId}"
        )
        assert delete_ep.deprecated is True

    def test_grouped_endpoints(self, sample_spec: OpenAPISpec):
        grouped = sample_spec.grouped_endpoints
        assert "pets" in grouped
        assert len(grouped["pets"]) == 4


class TestDocGenerator:
    """Tests for DocGenerator."""

    def test_register_renderer(self, sample_spec: OpenAPISpec):
        gen = DocGenerator(sample_spec)
        gen.register_renderer("html", HTMLRenderer())
        assert "html" in gen._renderers

    def test_render_html(self, sample_spec: OpenAPISpec, tmp_output: Path):
        gen = DocGenerator(sample_spec)
        gen.register_renderer("html", HTMLRenderer())
        result = gen.render("html", tmp_output / "index.html")
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "Pet Store API" in content
        assert "List all pets" in content

    def test_render_markdown(self, sample_spec: OpenAPISpec, tmp_output: Path):
        gen = DocGenerator(sample_spec)
        gen.register_renderer("md", MarkdownRenderer())
        result = gen.render("md", tmp_output / "api.md")
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "# Pet Store API" in content
        assert "`GET` /pets" in content

    def test_render_all(self, sample_spec: OpenAPISpec, tmp_output: Path):
        gen = DocGenerator(sample_spec)
        gen.register_renderer("html", HTMLRenderer())
        gen.register_renderer("md", MarkdownRenderer())
        results = gen.render_all(tmp_output, formats=["html", "md"])
        assert "html" in results
        assert "md" in results
        assert results["html"].exists()
        assert results["md"].exists()

    def test_unknown_format_raises(self, sample_spec: OpenAPISpec, tmp_output: Path):
        gen = DocGenerator(sample_spec)
        with pytest.raises(ValueError, match="Unknown format"):
            gen.render("xml", tmp_output / "out.xml")


class TestHTMLRenderer:
    """Tests for HTMLRenderer."""

    def test_render_creates_file(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html")
        assert result.exists()

    def test_render_contains_endpoints(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html")
        content = result.read_text(encoding="utf-8")
        assert "GET" in content
        assert "/pets" in content
        assert "List all pets" in content

    def test_render_contains_try_it(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html")
        content = result.read_text(encoding="utf-8")
        assert "tryEndpoint" in content
        assert "Interactive API Explorer" in content

    def test_render_contains_schemas(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html")
        content = result.read_text(encoding="utf-8")
        assert "Pet" in content
        assert "Schemas" in content

    def test_dark_theme(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html", theme="dark")
        content = result.read_text(encoding="utf-8")
        assert "#0f172a" in content  # dark bg color

    def test_corporate_theme(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = HTMLRenderer()
        result = renderer.render(sample_spec, tmp_output / "index.html", theme="corporate")
        content = result.read_text(encoding="utf-8")
        assert "Georgia" in content


class TestMarkdownRenderer:
    """Tests for MarkdownRenderer."""

    def test_render_creates_file(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = MarkdownRenderer()
        result = renderer.render(sample_spec, tmp_output / "api.md")
        assert result.exists()

    def test_render_contains_title(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = MarkdownRenderer()
        result = renderer.render(sample_spec, tmp_output / "api.md")
        content = result.read_text(encoding="utf-8")
        assert "# Pet Store API" in content

    def test_render_contains_endpoints(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = MarkdownRenderer()
        result = renderer.render(sample_spec, tmp_output / "api.md")
        content = result.read_text(encoding="utf-8")
        assert "`GET` /pets" in content
        assert "`POST` /pets" in content

    def test_render_contains_schemas(self, sample_spec: OpenAPISpec, tmp_output: Path):
        renderer = MarkdownRenderer()
        result = renderer.render(sample_spec, tmp_output / "api.md")
        content = result.read_text(encoding="utf-8")
        assert "## Schemas" in content
        assert "### Pet" in content


class TestSpecComparator:
    """Tests for SpecComparator."""

    def test_no_changes(self, sample_spec: OpenAPISpec):
        comparator = SpecComparator()
        result = comparator.compare(sample_spec, sample_spec)
        assert len(result.changes) == 0
        assert result.is_compatible is True

    def test_added_endpoint(self, sample_spec: OpenAPISpec):
        import copy
        spec_b = OpenAPISpec(
            title=sample_spec.title,
            version="1.1.0",
            description=sample_spec.description,
            base_url=sample_spec.base_url,
            endpoints=list(sample_spec.endpoints),
            schemas=dict(sample_spec.schemas),
            raw=dict(sample_spec.raw),
        )
        spec_b.endpoints.append(APIEndpoint(
            method="PATCH",
            path="/pets/{petId}",
            summary="Update a pet",
            tags=["pets"],
        ))

        comparator = SpecComparator()
        result = comparator.compare(sample_spec, spec_b)
        assert len(result.changes) > 0
        assert any(c.change_type == ChangeType.ADDED for c in result.changes)
        assert result.is_compatible is True

    def test_removed_endpoint(self, sample_spec: OpenAPISpec):
        import copy
        spec_b = OpenAPISpec(
            title=sample_spec.title,
            version="2.0.0",
            description=sample_spec.description,
            base_url=sample_spec.base_url,
            endpoints=[e for e in sample_spec.endpoints if e.method != "DELETE"],
            schemas=dict(sample_spec.schemas),
            raw=dict(sample_spec.raw),
        )

        comparator = SpecComparator()
        result = comparator.compare(sample_spec, spec_b)
        assert any(c.change_type == ChangeType.REMOVED for c in result.changes)
        assert result.is_compatible is False

    def test_deprecated_endpoint(self, sample_spec: OpenAPISpec):
        import copy
        spec_b = OpenAPISpec(
            title=sample_spec.title,
            version="1.1.0",
            description=sample_spec.description,
            base_url=sample_spec.base_url,
            endpoints=[
                APIEndpoint(
                    method=e.method,
                    path=e.path,
                    summary=e.summary,
                    description=e.description,
                    operation_id=e.operation_id,
                    parameters=e.parameters,
                    request_body=e.request_body,
                    responses=e.responses,
                    tags=e.tags,
                    deprecated=True if (e.method == "GET" and e.path == "/pets") else e.deprecated,
                )
                for e in sample_spec.endpoints
            ],
            schemas=dict(sample_spec.schemas),
            raw=dict(sample_spec.raw),
        )

        comparator = SpecComparator()
        result = comparator.compare(sample_spec, spec_b)
        assert any(c.change_type == ChangeType.DEPRECATED for c in result.changes)

    def test_summary_output(self, sample_spec: OpenAPISpec):
        comparator = SpecComparator()
        result = comparator.compare(sample_spec, sample_spec)
        summary = result.summary()
        assert "Pet Store API" in summary
        assert "Total changes: 0" in summary


class TestThemeManager:
    """Tests for ThemeManager."""

    def test_get_builtin_theme(self):
        manager = ThemeManager()
        theme = manager.get_theme("default")
        assert theme.name == "default"
        assert theme.primary_color == "#2563eb"

    def test_get_dark_theme(self):
        manager = ThemeManager()
        theme = manager.get_theme("dark")
        assert theme.name == "dark"
        assert theme.primary_color == "#60a5fa"

    def test_list_themes(self):
        manager = ThemeManager()
        themes = manager.list_themes()
        assert "default" in themes
        assert "dark" in themes
        assert "corporate" in themes

    def test_create_custom_theme(self, tmp_path: Path):
        manager = ThemeManager(theme_dir=tmp_path)
        config = ThemeConfig(name="custom", primary_color="#ff0000")
        path = manager.create_theme("custom", config)
        assert path.exists()
        assert path.read_text(encoding="utf-8").find("#ff0000") != -1

    def test_unknown_theme_returns_default(self):
        manager = ThemeManager()
        theme = manager.get_theme("nonexistent")
        assert theme.name == "default"


class TestSwagger2Support:
    """Tests for Swagger 2.0 spec support."""

    def test_parse_swagger_2(self):
        swagger_spec = {
            "swagger": "2.0",
            "info": {"title": "Legacy API", "version": "1.0"},
            "host": "api.example.com",
            "basePath": "/v1",
            "schemes": ["https"],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List users",
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
            "definitions": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                }
            },
        }
        parser = OpenAPIParser()
        spec = parser.parse(json.dumps(swagger_spec))
        assert spec.title == "Legacy API"
        assert len(spec.endpoints) == 1
        assert "User" in spec.schemas
