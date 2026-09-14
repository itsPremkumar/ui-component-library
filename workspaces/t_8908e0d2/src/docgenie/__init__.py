"""DocGenie — Automated API Documentation Generator."""

__version__ = "1.0.0"
__author__ = "Prem Kumar"

from docgenie.core import DocGenerator, OpenAPISpec
from docgenie.parsers.openapi import OpenAPIParser
from docgenie.renderers.html import HTMLRenderer
from docgenie.renderers.markdown import MarkdownRenderer
from docgenie.renderers.pdf import PDFRenderer
from docgenie.comparator.diff import SpecComparator
from docgenie.themes.manager import ThemeManager

__all__ = [
    "DocGenerator",
    "OpenAPISpec",
    "OpenAPIParser",
    "HTMLRenderer",
    "MarkdownRenderer",
    "PDFRenderer",
    "SpecComparator",
    "ThemeManager",
    "__version__",
]
