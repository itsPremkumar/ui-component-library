"""HTML renderer with interactive API explorer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docgenie.core import OpenAPISpec


class HTMLRenderer:
    """Render API documentation as an interactive HTML page."""

    def render(self, spec: OpenAPISpec, output_path: Path, theme: str = "default", **kwargs: Any) -> Path:
        """Generate HTML documentation."""
        spec_json = json.dumps(spec.raw, indent=2)
        theme_css = self._get_theme_css(theme)
        html = self._build_html(spec, spec_json, theme_css)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def _build_html(self, spec: OpenAPISpec, spec_json: str, theme_css: str) -> str:
        """Build the complete HTML document."""
        endpoints_html = self._render_endpoints(spec)
        try_it_html = self._render_try_it(spec)
        schemas_html = self._render_schemas(spec)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{spec.title} — API Documentation</title>
<style>
{theme_css}
</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
<h1>{spec.title}</h1>
<p class="version">v{spec.version}</p>
<p class="description">{spec.description}</p>
<div class="nav-sections">
<a href="#overview">Overview</a>
<a href="#endpoints">Endpoints</a>
<a href="#try-it">Try It</a>
<a href="#schemas">Schemas</a>
<a href="#spec-raw">Raw Spec</a>
</div>
</nav>
<main class="content">
<section id="overview">
<h2>Overview</h2>
<p>{spec.description}</p>
<div class="meta">
<p><strong>Version:</strong> {spec.version}</p>
<p><strong>Base URL:</strong> {spec.base_url}</p>
<p><strong>Endpoints:</strong> {len(spec.endpoints)}</p>
</div>
</section>

<section id="endpoints">
<h2>Endpoints</h2>
{endpoints_html}
</section>

<section id="try-it">
<h2>Interactive API Explorer</h2>
{try_it_html}
</section>

<section id="schemas">
<h2>Schemas</h2>
{schemas_html}
</section>

<section id="spec-raw">
<h2>Raw Specification</h2>
<pre class="raw-spec"><code>{spec_json}</code></pre>
</section>
</main>
</div>
<script>
// Interactive API Explorer
async function tryEndpoint(method, path) {{
    const baseUrl = '{spec.base_url}';
    const url = baseUrl + path;
    const resultEl = document.getElementById('try-result');
    resultEl.innerHTML = '<p class="loading">Loading...</p>';
    try {{
        const response = await fetch(url, {{ method: method }});
        const data = await response.json().catch(() => ({{}}));
        resultEl.innerHTML = '<p>Status: ' + response.status + '</p><pre>' + JSON.stringify(data, null, 2) + '</pre>';
    }} catch (err) {{
        resultEl.innerHTML = '<p class="error">Error: ' + err.message + '</p>';
    }}
}}
</script>
</body>
</html>"""

    def _render_endpoints(self, spec: OpenAPISpec) -> str:
        """Render endpoint cards."""
        html_parts: list[str] = []
        grouped = spec.grouped_endpoints
        for tag, endpoints in sorted(grouped.items()):
            html_parts.append(f'<h3 class="tag">{tag}</h3>')
            for ep in endpoints:
                method_class = ep.method.lower()
                params_html = ""
                if ep.parameters:
                    params_html = '<div class="params"><h4>Parameters</h4><ul>'
                    for p in ep.parameters:
                        req = "required" if p.get("required") else "optional"
                        params_html += f'<li><code>{p.get("name")}</code> ({p.get("in", "?")}) — {req}: {p.get("description", "")}</li>'
                    params_html += "</ul></div>"

                responses_html = ""
                if ep.responses:
                    responses_html = '<div class="responses"><h4>Responses</h4>'
                    for code, resp in ep.responses.items():
                        responses_html += f'<span class="status-code">{code}</span> — {resp.get("description", "")}  '
                    responses_html += "</div>"

                deprecated = '<span class="deprecated-badge">DEPRECATED</span>' if ep.deprecated else ""

                html_parts.append(f"""
<div class="endpoint-card" id="{ep.operation_id or ep.path}">
<div class="endpoint-header">
<span class="method {method_class}">{ep.method}</span>
<code class="path">{ep.path}</code>
{deprecated}
</div>
<p class="summary">{ep.summary or ep.description}</p>
{params_html}
{responses_html}
</div>""")
        return "\n".join(html_parts)

    def _render_try_it(self, spec: OpenAPISpec) -> str:
        """Render the interactive try-it section."""
        html = '<div class="try-it-panel">'
        for ep in spec.endpoints[:20]:  # Limit interactive to first 20
            html += f"""
<div class="try-item">
<button onclick="tryEndpoint('{ep.method}', '{ep.path}')" class="btn-try">
{ep.method} {ep.path}
</button>
<span>{ep.summary}</span>
</div>"""
        html += '</div><div id="try-result" class="try-result"></div>'
        return html

    def _render_schemas(self, spec: OpenAPISpec) -> str:
        """Render schema definitions."""
        html_parts: list[str] = []
        for name, schema in spec.schemas.items():
            html_parts.append(f"""
<div class="schema-card">
<h4>{name}</h4>
<pre><code>{json.dumps(schema, indent=2)}</code></pre>
</div>""")
        return "\n".join(html_parts)

    def _get_theme_css(self, theme: str) -> str:
        """Return theme CSS."""
        themes = {
            "default": self._default_theme(),
            "dark": self._dark_theme(),
            "corporate": self._corporate_theme(),
        }
        return themes.get(theme, themes["default"])

    @staticmethod
    def _default_theme() -> str:
        return """
:root {
  --primary: #2563eb;
  --bg: #f8fafc;
  --surface: #ffffff;
  --text: #1e293b;
  --border: #e2e8f0;
  --code-bg: #f1f5f9;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 24px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.sidebar h1 { font-size: 1.25rem; color: var(--primary); }
.sidebar .version { font-size: 0.875rem; color: #64748b; margin-bottom: 12px; }
.sidebar .description { font-size: 0.875rem; margin-bottom: 20px; }
.nav-sections { display: flex; flex-direction: column; gap: 4px; }
.nav-sections a { text-decoration: none; color: var(--text); padding: 8px 12px; border-radius: 6px; }
.nav-sections a:hover { background: var(--code-bg); }
.content { padding: 32px; max-width: 900px; }
section { margin-bottom: 40px; }
h2 { font-size: 1.5rem; margin-bottom: 16px; color: var(--primary); }
h3.tag { font-size: 1.1rem; margin: 20px 0 12px; padding: 4px 12px; background: var(--primary); color: white; border-radius: 4px; display: inline-block; }
.endpoint-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.endpoint-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.method { padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; }
.method.get { background: #dbeafe; color: #1d4ed8; }
.method.post { background: #dcfce7; color: #16a34a; }
.method.put { background: #fef3c7; color: #ca8a04; }
.method.patch { background: #ffedd5; color: #ea580c; }
.method.delete { background: #fee2e2; color: #dc2626; }
.method.head, .method.options { background: #f3e8ff; color: #7c3aed; }
.path { font-family: monospace; font-size: 0.9rem; }
.summary { font-size: 0.9rem; color: #64748b; }
.deprecated-badge { background: #fee2e2; color: #dc2626; padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; }
.params, .responses { margin-top: 12px; font-size: 0.85rem; }
.params ul { list-style: none; padding-left: 0; }
.params li { padding: 4px 0; border-bottom: 1px solid var(--border); }
.status-code { font-family: monospace; font-weight: 700; color: var(--primary); margin-right: 4px; }
.try-it-panel { display: flex; flex-direction: column; gap: 8px; }
.try-item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; }
.btn-try { background: var(--primary); color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-family: monospace; font-size: 0.8rem; }
.btn-try:hover { opacity: 0.9; }
.try-result { margin-top: 16px; padding: 16px; background: var(--code-bg); border-radius: 6px; min-height: 60px; }
.try-result pre { white-space: pre-wrap; word-break: break-all; }
.schema-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.schema-card h4 { color: var(--primary); margin-bottom: 8px; }
.raw-spec { background: var(--code-bg); padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 0.8rem; }
.meta { display: flex; gap: 24px; margin-top: 16px; font-size: 0.9rem; }
code { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
pre { white-space: pre-wrap; }
"""

    @staticmethod
    def _dark_theme() -> str:
        return """
:root {
  --primary: #60a5fa;
  --bg: #0f172a;
  --surface: #1e293b;
  --text: #e2e8f0;
  --border: #334155;
  --code-bg: #020617;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
.layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 24px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.sidebar h1 { font-size: 1.25rem; color: var(--primary); }
.sidebar .version { font-size: 0.875rem; color: #94a3b8; margin-bottom: 12px; }
.sidebar .description { font-size: 0.875rem; margin-bottom: 20px; }
.nav-sections { display: flex; flex-direction: column; gap: 4px; }
.nav-sections a { text-decoration: none; color: var(--text); padding: 8px 12px; border-radius: 6px; }
.nav-sections a:hover { background: var(--code-bg); }
.content { padding: 32px; max-width: 900px; }
section { margin-bottom: 40px; }
h2 { font-size: 1.5rem; margin-bottom: 16px; color: var(--primary); }
h3.tag { font-size: 1.1rem; margin: 20px 0 12px; padding: 4px 12px; background: var(--primary); color: white; border-radius: 4px; display: inline-block; }
.endpoint-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.endpoint-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.method { padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; }
.method.get { background: #1e3a5f; color: #60a5fa; }
.method.post { background: #14532d; color: #4ade80; }
.method.put { background: #713f12; color: #fbbf24; }
.method.delete { background: #7f1d1d; color: #f87171; }
.method.patch { background: #7c2d12; color: #fb923c; }
.path { font-family: monospace; font-size: 0.9rem; }
.summary { font-size: 0.9rem; color: #94a3b8; }
.deprecated-badge { background: #7f1d1d; color: #fca5a5; padding: 1px 6px; border-radius: 3px; font-size: 0.7rem; }
.params, .responses { margin-top: 12px; font-size: 0.85rem; }
.params ul { list-style: none; padding-left: 0; }
.params li { padding: 4px 0; border-bottom: 1px solid var(--border); }
.status-code { font-family: monospace; font-weight: 700; color: var(--primary); margin-right: 4px; }
.try-it-panel { display: flex; flex-direction: column; gap: 8px; }
.try-item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; }
.btn-try { background: var(--primary); color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-family: monospace; font-size: 0.8rem; }
.btn-try:hover { opacity: 0.9; }
.try-result { margin-top: 16px; padding: 16px; background: var(--code-bg); border-radius: 6px; min-height: 60px; }
.try-result pre { white-space: pre-wrap; word-break: break-all; }
.schema-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.schema-card h4 { color: var(--primary); margin-bottom: 8px; }
.raw-spec { background: var(--code-bg); padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 0.8rem; }
.meta { display: flex; gap: 24px; margin-top: 16px; font-size: 0.9rem; }
code { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
pre { white-space: pre-wrap; }
"""

    @staticmethod
    def _corporate_theme() -> str:
        return """
:root {
  --primary: #1a365d;
  --bg: #ffffff;
  --surface: #f7fafc;
  --text: #2d3748;
  --border: #cbd5e0;
  --code-bg: #edf2f7;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--text); }
.layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar { background: var(--surface); border-right: 1px solid var(--border); padding: 24px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.sidebar h1 { font-size: 1.25rem; color: var(--primary); }
.sidebar .version { font-size: 0.875rem; color: #718096; margin-bottom: 12px; }
.sidebar .description { font-size: 0.875rem; margin-bottom: 20px; }
.nav-sections { display: flex; flex-direction: column; gap: 4px; }
.nav-sections a { text-decoration: none; color: var(--text); padding: 8px 12px; border-radius: 6px; }
.nav-sections a:hover { background: var(--code-bg); }
.content { padding: 32px; max-width: 900px; }
section { margin-bottom: 40px; }
h2 { font-size: 1.5rem; margin-bottom: 16px; color: var(--primary); }
h3.tag { font-size: 1.1rem; margin: 20px 0 12px; padding: 4px 12px; background: var(--primary); color: white; border-radius: 4px; display: inline-block; }
.endpoint-card { background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 16px; margin-bottom: 12px; }
.endpoint-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.method { padding: 2px 8px; border-radius: 2px; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; font-family: monospace; }
.method.get { background: #c6f6d5; color: #276749; }
.method.post { background: #bee3f8; color: #2a4365; }
.method.put { background: #fefcbf; color: #744210; }
.method.delete { background: #fed7d7; color: #9b2c2c; }
.method.patch { background: #e9d8fd; color: #553c9a; }
.path { font-family: monospace; font-size: 0.9rem; }
.summary { font-size: 0.9rem; color: #718096; }
.deprecated-badge { background: #fed7d7; color: #9b2c2c; padding: 1px 6px; border-radius: 2px; font-size: 0.7rem; }
.params, .responses { margin-top: 12px; font-size: 0.85rem; }
.params ul { list-style: none; padding-left: 0; }
.params li { padding: 4px 0; border-bottom: 1px solid var(--border); }
.status-code { font-family: monospace; font-weight: 700; color: var(--primary); margin-right: 4px; }
.try-it-panel { display: flex; flex-direction: column; gap: 8px; }
.try-item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; }
.btn-try { background: var(--primary); color: white; border: none; padding: 6px 14px; border-radius: 2px; cursor: pointer; font-family: monospace; font-size: 0.8rem; }
.btn-try:hover { opacity: 0.9; }
.try-result { margin-top: 16px; padding: 16px; background: var(--code-bg); border-radius: 4px; min-height: 60px; }
.try-result pre { white-space: pre-wrap; word-break: break-all; }
.schema-card { background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 16px; margin-bottom: 12px; }
.schema-card h4 { color: var(--primary); margin-bottom: 8px; }
.raw-spec { background: var(--code-bg); padding: 16px; border-radius: 4px; overflow-x: auto; font-size: 0.8rem; }
.meta { display: flex; gap: 24px; margin-top: 16px; font-size: 0.9rem; }
code { font-family: 'Courier New', monospace; }
pre { white-space: pre-wrap; }
"""
