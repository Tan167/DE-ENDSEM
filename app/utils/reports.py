from __future__ import annotations
from io import BytesIO
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import pandas as pd


def generate_pdf_report(
    title: str,
    kpis: Dict[str, str],
    sections: Dict[str, pd.DataFrame],
) -> bytes:
    """Generate a simple PDF report with KPIs and tabular summaries.
    Returns raw PDF bytes suitable for st.download_button.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, title)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 2.6 * cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y = height - 3.4 * cm

    # KPIs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Key Metrics:")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    for k, v in kpis.items():
        c.drawString(2.2 * cm, y, f"- {k}: {v}")
        y -= 0.5 * cm
        if y < 3 * cm:
            c.showPage(); y = height - 2 * cm

    # Sections tables
    for section, df in sections.items():
        y -= 0.4 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, section)
        y -= 0.6 * cm
        c.setFont("Helvetica", 9)
        if df is None or df.empty:
            c.drawString(2.2 * cm, y, "(No data)")
            y -= 0.5 * cm
        else:
            # Draw table-like rows (first few only)
            max_rows = 20
            # Prepare text rows
            cols = list(df.columns)
            c.drawString(2.2 * cm, y, " | ".join(str(cn) for cn in cols))
            y -= 0.5 * cm
            for _, row in df.head(max_rows).iterrows():
                line = " | ".join(str(row[c]) for c in cols)
                c.drawString(2.2 * cm, y, line[:110])
                y -= 0.45 * cm
                if y < 3 * cm:
                    c.showPage(); y = height - 2 * cm
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(2 * cm, y, f"(cont.) {section}")
                    y -= 0.6 * cm
                    c.setFont("Helvetica", 9)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
