"""Theme and branding manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ThemeConfig:
    """Theme configuration."""
    name: str = "default"
    primary_color: str = "#2563eb"
    background_color: str = "#f8fafc"
    text_color: str = "#1e293b"
    font_family: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    logo_url: str = ""
    custom_css: str = ""
    brand_name: str = ""
    footer_text: str = ""


class ThemeManager:
    """Manage documentation themes and branding."""

    BUILT_IN_THEMES = {
        "default": ThemeConfig(name="default"),
        "dark": ThemeConfig(
            name="dark",
            primary_color="#60a5fa",
            background_color="#0f172a",
            text_color="#e2e8f0",
        ),
        "corporate": ThemeConfig(
            name="corporate",
            primary_color="#1a365d",
            background_color="#ffffff",
            text_color="#2d3748",
            font_family="Georgia, 'Times New Roman', serif",
        ),
    }

    def __init__(self, theme_dir: Path | None = None):
        self.theme_dir = theme_dir or Path.home() / ".docgenie" / "themes"
        self.theme_dir.mkdir(parents=True, exist_ok=True)

    def get_theme(self, name: str) -> ThemeConfig:
        """Get a theme by name."""
        if name in self.BUILT_IN_THEMES:
            return self.BUILT_IN_THEMES[name]
        custom_path = self.theme_dir / f"{name}.css"
        if custom_path.exists():
            config = ThemeConfig(name=name, custom_css=custom_path.read_text(encoding="utf-8"))
            return config
        return self.BUILT_IN_THEMES["default"]

    def list_themes(self) -> list[str]:
        """List all available themes."""
        built_ins = list(self.BUILT_IN_THEMES.keys())
        customs = [f.stem for f in self.theme_dir.glob("*.css")]
        return sorted(set(built_ins + customs))

    def create_theme(self, name: str, config: ThemeConfig) -> Path:
        """Create a custom theme."""
        css = self._generate_css(config)
        theme_path = self.theme_dir / f"{name}.css"
        theme_path.write_text(css, encoding="utf-8")
        return theme_path

    @staticmethod
    def _generate_css(config: ThemeConfig) -> str:
        """Generate CSS from theme config."""
        return f""":root {{
  --primary: {config.primary_color};
  --bg: {config.background_color};
  --text: {config.text_color};
  --font: {config.font_family};
}}

body {{
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
}}

h1, h2, h3 {{
  color: var(--primary);
}}

{config.custom_css}
"""
