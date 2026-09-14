"""PDF renderer using fpdf2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docgenie.core import OpenAPISpec


class PDFRenderer:
    """Render API documentation as PDF."""

    def render(self, spec: OpenAPISpec, output_path: Path, theme: str = "default", **kwargs: Any) -> Path:
        """Generate PDF documentation."""
        try:
            from fpdf import FPDF
        except ImportError:
            raise ImportError("PDF rendering requires fpdf2: pip install fpdf2")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 15, spec.title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Version: {spec.version}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 8, f"Base URL: {spec.base_url}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # Description
        if spec.description:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, spec.description)
            pdf.ln(3)

        # Endpoints
        grouped = spec.grouped_endpoints
        for tag, endpoints in sorted(grouped.items()):
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, tag, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            for ep in endpoints:
                if pdf.get_y() > 250:
                    pdf.add_page()

                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, f"{ep.method} {ep.path}", new_x="LMARGIN", new_y="NEXT")

                if ep.deprecated:
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 6, "DEPRECATED", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)

                if ep.summary:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(0, 6, ep.summary, new_x="LMARGIN", new_y="NEXT")

                if ep.description:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.multi_cell(0, 5, ep.description)

                if ep.parameters:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 6, "Parameters:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 8)
                    for p in ep.parameters:
                        name = p.get("name", "")
                        param_in = p.get("in", "")
                        required = "required" if p.get("required") else "optional"
                        desc = p.get("description", "")
                        pdf.cell(0, 5, f"  - {name} ({param_in}, {required}): {desc}", new_x="LMARGIN", new_y="NEXT")

                if ep.responses:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 6, "Responses:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 8)
                    for code, resp in ep.responses.items():
                        desc = resp.get("description", "")
                        pdf.cell(0, 5, f"  - {code}: {desc}", new_x="LMARGIN", new_y="NEXT")

                pdf.ln(3)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(3)

        # Schemas
        if spec.schemas:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Schemas", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            for name, schema in spec.schemas.items():
                if pdf.get_y() > 250:
                    pdf.add_page()
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, name, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Courier", "", 8)
                schema_json = json.dumps(schema, indent=2)
                for line in schema_json.split("\n"):
                    pdf.cell(0, 4, line, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(4)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))
        return output_path
