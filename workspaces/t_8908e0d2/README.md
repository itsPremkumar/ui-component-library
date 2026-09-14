# DocGenie - Automated API Documentation Generator

**DocGenie** is a Python CLI and library that generates beautiful, interactive API documentation from OpenAPI 3.x and Swagger 2.x specifications. Output to HTML, Markdown, or PDF with customizable themes and built-in version comparison.

## Features

- **Multiple Output Formats** — HTML, Markdown, PDF
- **Interactive API Explorer** — try endpoints directly from the generated docs
- **OpenAPI 3.x & Swagger 2.0** — supports both versions
- **Version Comparison** — diff two spec revisions with breaking-change detection
- **Customizable Themes** — built-in themes (default, dark, corporate) + custom CSS
- **CLI & Library** — use from the command line or as a Python library

## Installation

```bash
pip install docgenie
```

Or with PDF support:
```bash
pip install docgenie[pdf]
```

## Quick Start

### CLI

```bash
# Generate HTML docs
docgenie generate petstore.json -f html -o ./docs

# Generate all formats
docgenie generate petstore.json -f all -o ./docs

# Use a theme
docgenie generate petstore.json -f html -t dark -o ./docs-dark

# Compare two API versions
docgenie compare petstore-v1.json petstore-v2.json

# Show spec info
docgenie info petstore.json

# List available themes
docgenie themes

# Create a custom theme
docgenie create_theme my-theme --primary-color "#ff6600" --brand "MyCorp"
```

### Library

```python
from docgenie import DocGenerator, OpenAPIParser
from docgenie.renderers.html import HTMLRenderer

parser = OpenAPIParser()
spec = parser.parse("petstore.json")

gen = DocGenerator(spec, theme="dark")
gen.register_renderer("html", HTMLRenderer())
gen.render("html", Path("./docs/index.html"))
```

## CLI Commands

### `generate` — Generate documentation

```
docgenie generate SPEC [OPTIONS]

Options:
  -f, --format [html|md|pdf|all]  Output format (repeatable)
  -o, --output PATH                Output directory (default: ./docs)
  -t, --theme TEXT                 Theme name (default: default)
  --base-url TEXT                  Override base URL
```

### `compare` — Compare two API versions

```
docgenie compare SPEC_A SPEC_B [OPTIONS]

Options:
  -f, --format [text|json]   Output format
```

Shows added/removed endpoints, parameter changes, schema modifications, and deprecations. Highlights breaking changes.

### `info` — Show spec summary

```
docgenie info SPEC
```

### `themes` — List available themes

```
docgenie themes
```

### `create-theme` — Create a custom theme

```
docgenie create-theme NAME [OPTIONS]

Options:
  --primary-color TEXT
  --bg-color TEXT
  --text-color TEXT
  --font TEXT
  --brand TEXT
  --footer TEXT
```

## Theme Customization

### Built-in Themes

| Theme      | Primary | Background | Use Case              |
|------------|---------|------------|-----------------------|
| `default`  | #2563eb | #f8fafc    | General purpose       |
| `dark`     | #60a5fa | #0f172a    | Developer portals     |
| `corporate`| #1a365d | #ffffff    | Enterprise/formal     |

### Custom CSS Theme

1. Create a CSS file at `~/.docgenie/themes/<name>.css`
2. Use it: `docgenie generate spec.json -t <name>`

Example custom theme (`~/.docgenie/themes/acme.css`):
```css
:root {
  --primary: #ff6600;
  --bg: #f0f0f0;
  --text: #333;
  --font: 'Segoe UI', sans-serif;
}
```

### CLI Theme Creation

```bash
docgenie create-theme acme \
  --primary-color "#ff6600" \
  --bg-color "#f0f0f0" \
  --brand "ACME Corp" \
  --footer "© 2024 ACME Corp. All rights reserved."
```

## Output Samples

### HTML Output
- Responsive layout with sidebar navigation
- Color-coded HTTP methods (GET=blue, POST=green, etc.)
- Interactive "Try It" panel with fetch calls
- Schema viewer with syntax highlighting
- Raw spec viewer

### Markdown Output
- GitHub-compatible markdown
- Tables for parameters
- Code blocks for schemas
- Table of contents with anchor links

### PDF Output
- Multi-page document with headers/footers
- Proper page breaks between sections
- Monospace font for schemas
- Professional formatting

## API Version Comparison

DocGenie can compare two OpenAPI specs and identify:

| Change Type  | Description                  |
|-------------|------------------------------|
| Added       | New endpoints, schemas       |
| Removed     | Deleted endpoints, schemas   |
| Modified    | Changed descriptions, types  |
| Deprecated  | Marked as deprecated         |

Breaking changes (removed endpoints/schemas) are highlighted, and the tool reports whether the change is backward compatible.

```bash
docgenie compare v1.json v2.json
# Output:
# Comparing Pet Store API 1.0.0 → Pet Store API 2.0.0
# Total changes: 3
#   Added: 2
#   Removed: 1
#   Modified: 0
#   Deprecated: 0
# Breaking changes: 1
# Backward compatible: No
```

## Architecture

```
docgenie/
├── core.py              # DocGenerator, OpenAPISpec, APIEndpoint
├── cli.py               # Click CLI interface
├── parsers/
│   └── openapi.py       # OpenAPI 3.x / Swagger 2.0 parser
├── renderers/
│   ├── html.py          # HTML renderer with interactive explorer
│   ├── markdown.py      # Markdown renderer
│   └── pdf.py           # PDF renderer (fpdf2)
├── themes/
│   └── manager.py       # Theme management
└── comparator/
    └── diff.py          # Version comparison engine
```

## Requirements

- Python 3.9+
- click >= 8.0
- rich >= 13.0
- pyyaml >= 6.0
- fpdf2 >= 2.7 (for PDF output)

## License

MIT
