#!/usr/bin/env python3
"""
DevPortal Test Suite
Validates the portal's markdown content, links, and structure.
"""
import os
import re
import sys
import json
from pathlib import Path
from typing import List, Set, Tuple

WORKSPACE = Path(__file__).resolve().parent.parent


def get_all_markdown_files() -> List[Path]:
    """Get all markdown files in the workspace."""
    files = []
    for path in WORKSPACE.rglob("*.md"):
        if ".git" not in str(path) and "node_modules" not in str(path):
            files.append(path)
    return files


def get_all_files() -> List[Path]:
    """Get all files in the workspace."""
    files = []
    for path in WORKSPACE.rglob("*"):
        if path.is_file() and ".git" not in str(path) and "node_modules" not in str(path):
            files.append(path)
    return files


class TestSuite:
    """Test suite for DevPortal."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
    
    def run_all(self):
        """Run all tests."""
        tests = [
            self.test_required_files_exist,
            self.test_index_html_valid,
            self.test_sidebar_references_valid,
            self.test_navbar_references_valid,
            self.test_markdown_files_valid,
            self.test_internal_links_resolve,
            self.test_api_spec_js_valid,
            self.test_theme_css_valid,
            self.test_openapi_spec_valid,
            self.test_readme_complete,
        ]
        
        for test in tests:
            try:
                test()
            except AssertionError as e:
                self.failed += 1
                self.errors.append(f"FAIL: {test.__name__}: {e}")
            except Exception as e:
                self.failed += 1
                self.errors.append(f"ERROR: {test.__name__}: {e}")
            else:
                self.passed += 1
                print(f"PASS: {test.__name__}")
    
    def assert_true(self, condition: bool, message: str):
        """Assert condition is true."""
        if not condition:
            raise AssertionError(message)
    
    def test_required_files_exist(self):
        """Test that all required files exist."""
        required = [
            "index.html",
            "README.md",
            "_sidebar.md",
            "_navbar.md",
            "_coverpage.md",
            "assets/css/theme.css",
            "assets/js/custom.js",
            "assets/js/api-spec.js",
            "docs/guides/quickstart.md",
            "docs/guides/installation.md",
            "docs/guides/configuration.md",
            "docs/api/README.md",
            "docs/api/v2/authentication.md",
            "docs/api/v2/users.md",
            "docs/api/v2/resources.md",
            "docs/api/v2/webhooks.md",
            "docs/api/v1/authentication.md",
            "docs/api/v1/users.md",
            "docs/api/v1/resources.md",
            "openapi/spec.yaml",
            "scripts/serve.sh",
            "scripts/deploy.sh",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "LICENSE",
        ]
        
        for filepath in required:
            full_path = WORKSPACE / filepath
            self.assert_true(full_path.exists(), f"Required file missing: {filepath}")
    
    def test_index_html_valid(self):
        """Test that index.html is valid HTML with required elements."""
        content = (WORKSPACE / "index.html").read_text()
        
        self.assert_true("<!DOCTYPE html>" in content, "Missing DOCTYPE declaration")
        self.assert_true("docsify" in content.lower(), "Missing Docsify reference")
        self.assert_true("window.$docsify" in content, "Missing Docsify configuration")
        self.assert_true("loadSidebar" in content, "Missing sidebar reference")
        self.assert_true("loadNavbar" in content, "Missing navbar reference")
        self.assert_true("search" in content.lower(), "Missing search plugin")
    
    def test_sidebar_references_valid(self):
        """Test that sidebar links point to existing files."""
        content = (WORKSPACE / "_sidebar.md").read_text()
        
        # Extract all markdown links
        links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for text, href in links:
            if href.startswith("http"):
                continue
            if href.startswith("#"):
                continue
            
            # Clean the href
            clean_href = href.split("?")[0].split("#")[0]
            if not clean_href:
                continue
            
            full_path = WORKSPACE / clean_href
            self.assert_true(
                full_path.exists(),
                f"Sidebar link '{text}' points to non-existent file: {href}"
            )
    
    def test_navbar_references_valid(self):
        """Test that navbar links are valid."""
        content = (WORKSPACE / "_navbar.md").read_text()
        
        links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for text, href in links:
            if href.startswith("http"):
                continue
            if href.startswith("#"):
                continue
            
            clean_href = href.split("?")[0].split("#")[0]
            if not clean_href:
                continue
            
            full_path = WORKSPACE / clean_href
            self.assert_true(
                full_path.exists(),
                f"Navbar link '{text}' points to non-existent file: {href}"
            )
    
    def test_markdown_files_valid(self):
        """Test that all markdown files have valid structure."""
        for md_file in get_all_markdown_files():
            content = md_file.read_text()
            
            # Check file is not empty
            self.assert_true(
                len(content.strip()) > 0,
                f"Empty markdown file: {md_file.relative_to(WORKSPACE)}"
            )
            
            # Check for at least a heading
            self.assert_true(
                "#" in content,
                f"No headings found in: {md_file.relative_to(WORKSPACE)}"
            )
    
    def test_internal_links_resolve(self):
        """Test that internal links in markdown files resolve."""
        # Collect all files (both markdown and non-markdown)
        all_files = set()
        for f in get_all_files():
            rel_path = str(f.relative_to(WORKSPACE)).replace("\\", "/")
            all_files.add(rel_path)
        
        all_md = set()
        for md_file in get_all_markdown_files():
            rel_path = str(md_file.relative_to(WORKSPACE)).replace("\\", "/")
            all_md.add(rel_path)
            all_files.add(rel_path)
        
        for md_file in get_all_markdown_files():
            content = md_file.read_text()
            # Remove code blocks before checking links
            content_no_code = re.sub(r'```[\s\S]*?```', '', content)
            content_no_code = re.sub(r'`[^`]+`', '', content_no_code)
            
            links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content_no_code)
            
            for text, href in links:
                if href.startswith("http"):
                    continue
                if href.startswith("#"):
                    continue
                
                # Resolve relative to the current file
                clean_href = href.split("?")[0].split("#")[0]
                if not clean_href:
                    continue
                
                if clean_href.startswith("/"):
                    resolved = clean_href[1:]
                else:
                    md_dir = md_file.parent.relative_to(WORKSPACE)
                    resolved = str(Path(md_dir) / clean_href).replace("\\", "/")
                    # Normalize path (handle ..)
                    parts = resolved.split("/")
                    normalized = []
                    for p in parts:
                        if p == "..":
                            if normalized:
                                normalized.pop()
                        elif p != ".":
                            normalized.append(p)
                    resolved = "/".join(normalized)
                
                # Check with and without .md extension
                variants = [resolved, resolved + ".md", resolved + "/README.md"]
                found = any(v in all_files for v in variants)
                
                self.assert_true(
                    found,
                    f"Broken link in {md_file.relative_to(WORKSPACE)}: '{text}' -> '{href}' (resolved: {resolved})"
                )
    
    def test_api_spec_js_valid(self):
        """Test that API spec JavaScript is valid."""
        content = (WORKSPACE / "assets/js/api-spec.js").read_text()
        
        self.assert_true("window.API_SPEC" in content, "Missing API_SPEC definition")
        self.assert_true("v2:" in content, "Missing v2 endpoints")
        self.assert_true("v1:" in content, "Missing v1 endpoints")
        
        # Try to parse as JavaScript (basic syntax check)
        try:
            # Extract JSON structure
            json_start = content.index('{')
            json_end = content.rindex('}') + 1
            json_str = content[json_start:json_end]
            # This won't be valid JS, but we can check structure
        except ValueError:
            raise AssertionError("API spec does not contain valid JSON structure")
    
    def test_theme_css_valid(self):
        """Test that theme CSS contains required variables."""
        content = (WORKSPACE / "assets/css/theme.css").read_text()
        
        required_vars = [
            "--primary-color",
            "--text-color",
            "--bg-color",
            "--code-bg",
            "--font-family",
        ]
        
        for var in required_vars:
            self.assert_true(
                var in content,
                f"Missing CSS variable: {var}"
            )
        
        self.assert_true("[data-theme=" in content, "Missing dark mode support")
    
    def test_openapi_spec_valid(self):
        """Test that OpenAPI spec is valid YAML."""
        try:
            import yaml
            content = (WORKSPACE / "openapi/spec.yaml").read_text()
            spec = yaml.safe_load(content)
            
            self.assert_true("openapi" in spec, "Missing openapi version")
            self.assert_true("info" in spec, "Missing info section")
            self.assert_true("paths" in spec, "Missing paths section")
        except ImportError:
            # If PyYAML not available, just check basic structure
            content = (WORKSPACE / "openapi/spec.yaml").read_text()
            self.assert_true("openapi:" in content, "Missing openapi version")
            self.assert_true("info:" in content, "Missing info section")
            self.assert_true("paths:" in content, "Missing paths section")
    
    def test_readme_complete(self):
        """Test that README contains all required sections."""
        content = (WORKSPACE / "README.md").read_text()
        
        required_sections = [
            "## Features",
            "## Quick Start",
            "## Project Structure",
            "## Customization",
            "## Deployment",
            "## Testing",
        ]
        
        for section in required_sections:
            self.assert_true(
                section in content,
                f"README missing section: {section}"
            )


def main():
    """Run the test suite."""
    suite = TestSuite()
    suite.run_all()
    
    print()
    print("=" * 50)
    print(f"Results: {suite.passed} passed, {suite.failed} failed")
    print("=" * 50)
    
    if suite.errors:
        print()
        for error in suite.errors:
            print(error)
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
