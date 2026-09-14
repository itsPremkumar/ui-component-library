"""IaC parsers for extracting resources from various formats."""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from infrascan.schemas import Resource, ResourceType


class BaseParser(ABC):
    """Abstract base parser for IaC files."""

    @abstractmethod
    def parse(self, file_path: Path) -> list[Resource]:
        """Parse a file and return extracted resources."""
        ...

    @abstractmethod
    def detect(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        ...


class TerraformParser(BaseParser):
    """Parser for Terraform (.tf) files."""

    RESOURCE_PATTERN = re.compile(
        r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{',
        re.MULTILINE,
    )
    PROP_PATTERN = re.compile(
        r'(\w+)\s*=\s*(.+?)(?:\n|$)',
        re.MULTILINE,
    )

    def detect(self, file_path: Path) -> bool:
        return file_path.suffix == ".tf"

    def parse(self, file_path: Path) -> list[Resource]:
        content = file_path.read_text(encoding="utf-8")
        resources = []

        for match in self.RESOURCE_PATTERN.finditer(content):
            resource_type = match.group(1)
            resource_name = match.group(2)
            start_pos = match.start()
            line_start = content[:start_pos].count("\n") + 1
            block_start = match.end() - 1
            block_end = self._find_block_end(content, block_start)
            block_content = content[block_start:block_end]
            line_end = content[:block_end].count("\n") + 1

            properties: dict[str, Any] = {}
            for prop_match in self.PROP_PATTERN.finditer(block_content):
                key = prop_match.group(1).strip()
                value = prop_match.group(2).strip().strip('"').strip("'")
                if key and key not in ("resource", "module", "variable", "output", "data"):
                    properties[key] = value

            resources.append(Resource(
                name=resource_name,
                resource_type=resource_type,
                source_file=str(file_path),
                line_start=line_start,
                line_end=line_end,
                properties=properties,
                iac_type=ResourceType.TERRAFORM,
            ))

        return resources

    def _find_block_end(self, content: str, start: int) -> int:
        depth = 0
        pos = start
        while pos < len(content):
            if content[pos] == "{":
                depth += 1
            elif content[pos] == "}":
                depth -= 1
                if depth == 0:
                    return pos + 1
            pos += 1
        return len(content)


class CloudFormationParser(BaseParser):
    """Parser for AWS CloudFormation (YAML/JSON) templates."""

    def detect(self, file_path: Path) -> bool:
        if file_path.suffix not in (".yaml", ".yml", ".json"):
            return False
        try:
            content = file_path.read_text(encoding="utf-8")
            if file_path.suffix == ".json":
                data = json.loads(content)
            else:
                data = yaml.safe_load(content)
            return isinstance(data, dict) and "Resources" in data
        except (json.JSONDecodeError, yaml.YAMLError, OSError):
            return False

    def parse(self, file_path: Path) -> list[Resource]:
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix == ".json":
            data = json.loads(content)
        else:
            data = yaml.safe_load(content)

        resources = []
        raw_resources = data.get("Resources", {})

        for name, definition in raw_resources.items():
            if not isinstance(definition, dict):
                continue
            resource_type = definition.get("Type", "AWS::CloudFormation::Custom::Resource")
            properties = definition.get("Properties", {})
            line_start = self._find_resource_line(content, name)

            resources.append(Resource(
                name=name,
                resource_type=resource_type,
                source_file=str(file_path),
                line_start=line_start,
                line_end=line_start,
                properties=properties if isinstance(properties, dict) else {},
                iac_type=ResourceType.CLOUDFORMATION,
            ))

        return resources

    def _find_resource_line(self, content: str, resource_name: str) -> int:
        for i, line in enumerate(content.split("\n"), 1):
            if resource_name in line and not line.strip().startswith("#"):
                return i
        return 0


class PulumiParser(BaseParser):
    """Parser for Pulumi YAML files."""

    def detect(self, file_path: Path) -> bool:
        if file_path.suffix not in (".yaml", ".yml"):
            return False
        try:
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            return isinstance(data, dict) and data.get("runtime") == "python" and isinstance(data.get("resources"), dict)
        except (yaml.YAMLError, OSError):
            return False

    def parse(self, file_path: Path) -> list[Resource]:
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        resources = []

        raw_resources = data.get("resources", {})
        for name, definition in raw_resources.items():
            if not isinstance(definition, dict):
                continue
            resource_type = definition.get("type", "pulumi:unknown")
            properties = definition.get("properties", {})

            resources.append(Resource(
                name=name,
                resource_type=resource_type,
                source_file=str(file_path),
                line_start=0,
                line_end=0,
                properties=properties if isinstance(properties, dict) else {},
                iac_type=ResourceType.PULUMI,
            ))

        return resources


class GenericParser(BaseParser):
    """Generic fallback parser."""

    def detect(self, file_path: Path) -> bool:
        return True

    def parse(self, file_path: Path) -> list[Resource]:
        return [Resource(
            name=file_path.stem,
            resource_type="unknown",
            source_file=str(file_path),
            iac_type=ResourceType.GENERIC,
        )]


class ParserRegistry:
    """Registry of parsers, selects the right one for each file."""

    def __init__(self):
        self._parsers: list[BaseParser] = [
            TerraformParser(),
            CloudFormationParser(),
            PulumiParser(),
            GenericParser(),
        ]

    def get_parser(self, file_path: Path) -> BaseParser:
        for parser in self._parsers:
            if parser.detect(file_path):
                return parser
        return self._parsers[-1]

    def parse_file(self, file_path: Path) -> list[Resource]:
        parser = self.get_parser(file_path)
        try:
            return parser.parse(file_path)
        except Exception:
            return [Resource(
                name=file_path.stem,
                resource_type="parse_error",
                source_file=str(file_path),
                iac_type=ResourceType.GENERIC,
            )]

    def scan_directory(self, directory: Path) -> list[Resource]:
        all_resources: list[Resource] = []
        for path in sorted(directory.rglob("*")):
            if path.is_file() and self._is_iac_file(path):
                all_resources.extend(self.parse_file(path))
        return all_resources

    @staticmethod
    def _is_iac_file(path: Path) -> bool:
        iac_extensions = {".tf", ".tfvars", ".tfplan", ".yaml", ".yml", ".json"}
        if path.suffix in iac_extensions:
            return True
        if "Pulumi" in path.name:
            return True
        return False
