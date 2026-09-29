"""Render the final MEACompass technical report from its reviewed Markdown."""

from __future__ import annotations

import html
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "report_draft.md"
OUTPUT = ROOT / "docs" / "MEACompass_Technical_Report.pdf"
ACCENT = colors.HexColor("#1D6F72")
NAVY = colors.HexColor("#102A43")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
PALE = colors.HexColor("#E8F4F4")

PAGE_BREAK_HEADINGS = {
    "1. Problem and importance",
    "3. Data and audit",
    "4. Preregistered protocol",
    "5. Deviations and integrity audit",
    "8. Main results",
    "9. Calibration",
    "10. Selective prediction / abstention",
    "11. Time ablation",
    "13. Interpretability",
    "15. Adoption path for neural organ-on-chip research",
    "17. Ethics and compliance",
    "19. Reproduction",
    "21. Conclusion",
    "23. Appendix A — Endpoint and evidence map",
    "24. Appendix B — Registered status ledger",
}


def register_fonts() -> None:
    """Use the redistributable DejaVu fonts bundled with matplotlib."""
    from matplotlib import font_manager

    faces = {
        "DV": font_manager.findfont("DejaVu Sans"),
        "DV-Bold": font_manager.findfont(
            font_manager.FontProperties(family="DejaVu Sans", weight="bold")
        ),
        "DV-Mono": font_manager.findfont("DejaVu Sans Mono"),
    }
    for name, path in faces.items():
        pdfmetrics.registerFont(TTFont(name, path))


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r'<font name="DV-Mono">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(
        r"(?<![\">])(https?://[^\s<]+)",
        r'<link href="\1" color="#1D6F72">\1</link>',
        escaped,
    )
    return escaped


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="DV", fontSize=8.55,
            leading=11.4, textColor=INK, spaceAfter=5.5, alignment=TA_LEFT,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="DV-Bold", fontSize=16,
            leading=19, textColor=NAVY, spaceBefore=5, spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="DV-Bold", fontSize=10.5,
            leading=13, textColor=ACCENT, spaceBefore=7, spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["BodyText"], fontName="DV", fontSize=7.5,
            leading=9, textColor=MUTED, alignment=TA_CENTER, spaceAfter=6,
        ),
        "table": ParagraphStyle(
            "Table", parent=base["BodyText"], fontName="DV", fontSize=6.8,
            leading=8.3, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["BodyText"], fontName="DV-Bold", fontSize=6.7,
            leading=8.1, textColor=colors.white,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["BodyText"], fontName="DV-Mono", fontSize=7.5,
            leading=10, backColor=colors.HexColor("#F0F4F8"), borderPadding=5,
        ),
    }


def make_table(rows: list[list[str]], sty: dict[str, ParagraphStyle]) -> Table:
    rendered = []
    for row_index, row in enumerate(rows):
        style = sty["table_head"] if row_index == 0 else sty["table"]
        rendered.append([Paragraph(inline(cell.strip()), style) for cell in row])
    available = A4[0] - 32 * mm
    widths = [available / len(rendered[0])] * len(rendered[0])
    table = Table(rendered, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BCCCDC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ]
        )
    )
    return table


def parse_markdown(text: str) -> list[object]:
    sty = styles()
    lines = text.splitlines()
    story: list[object] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line or line.startswith("# ") or line.startswith("**Toward Functional"):
            index += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            if title in PAGE_BREAK_HEADINGS:
                story.append(PageBreak())
            story.append(Paragraph(inline(title), sty["h2"]))
            index += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:].strip()), sty["h3"]))
            index += 1
            continue
        image_match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if image_match:
            path = (SOURCE.parent / image_match.group(2)).resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Report figure is missing: {path}")
            pic = Image(str(path))
            max_width, max_height = A4[0] - 36 * mm, 78 * mm
            scale = min(max_width / pic.imageWidth, max_height / pic.imageHeight)
            pic.drawWidth, pic.drawHeight = pic.imageWidth * scale, pic.imageHeight * scale
            story.append(KeepTogether([pic, Paragraph(inline(image_match.group(1)), sty["caption"])]))
            index += 1
            continue
        if line.startswith("|"):
            raw_rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw_rows.append(lines[index].strip().strip("|").split("|"))
                index += 1
            if len(raw_rows) > 1 and all(
                re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in raw_rows[1]
            ):
                raw_rows.pop(1)
            story.extend([make_table(raw_rows, sty), Spacer(1, 5)])
            continue
        if line.startswith("```"):
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            story.append(Paragraph("<br/>".join(html.escape(x) for x in code), sty["code"]))
            continue
        if line.startswith("- "):
            items = []
            while index < len(lines) and lines[index].startswith("- "):
                parts = [lines[index][2:].strip()]
                index += 1
                while index < len(lines) and lines[index].startswith("  "):
                    parts.append(lines[index].strip())
                    index += 1
                items.append(ListItem(Paragraph(inline(" ".join(parts)), sty["body"])))
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=13, bulletFontName="DV"))
            continue
        paragraph = [line]
        index += 1
        while index < len(lines):
            candidate = lines[index].rstrip()
            if not candidate or candidate.startswith(("#", "|", "- ", "```", "![")):
                break
            paragraph.append(candidate.strip())
            index += 1
        story.append(Paragraph(inline(" ".join(paragraph)), sty["body"]))
    return story


def cover(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, height - 18 * mm, width, 18 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("DV-Bold", 30)
    canvas.drawString(24 * mm, height - 60 * mm, "MEACompass")
    canvas.setFont("DV-Bold", 17)
    title = [
        "Reliability-Aware Early Prediction of",
        "Neural Network Development from",
        "Microelectrode-Array Assays",
    ]
    y = height - 78 * mm
    for part in title:
        canvas.drawString(24 * mm, y, part)
        y -= 9 * mm
    canvas.setFillColor(colors.HexColor("#9FB3C8"))
    canvas.setFont("DV", 11)
    canvas.drawString(24 * mm, y - 8 * mm, "Toward Functional Digital Twins for Neural Organ-on-Chip Screening")
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(24 * mm, y - 17 * mm, 112 * mm, y - 17 * mm)
    canvas.setFont("DV", 8.5)
    canvas.drawString(24 * mm, 25 * mm, "Technical report • 29 September 2026")
    canvas.restoreState()


def body_page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(16 * mm, height - 14 * mm, width - 16 * mm, height - 14 * mm)
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, height - 10.5 * mm, "MEACompass • Technical report")
    canvas.drawRightString(width - 16 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


def build() -> int:
    register_fonts()
    text = SOURCE.read_text(encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=18 * mm, bottomMargin=16 * mm,
        title="MEACompass: Reliability-Aware Early Prediction of Neural Network Development from Microelectrode-Array Assays",
        author="Ziyad Azzaz",
        subject="AI4S competition technical report",
    )
    cover_frame = Frame(0, 0, A4[0], A4[1], id="cover")
    body_frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=[cover_frame], onPage=cover, autoNextPageTemplate="Body"),
            PageTemplate(id="Body", frames=[body_frame], onPage=body_page),
        ]
    )
    story = [Spacer(1, A4[1] - 5 * mm), PageBreak(), *parse_markdown(text)]
    doc.build(story)
    reader = PdfReader(str(OUTPUT))
    pages = len(reader.pages)
    if not 12 <= pages <= 18:
        raise RuntimeError(f"PDF has {pages} pages; required total is 12–18")
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = [
        "MEACompass", "Team information", "Calibration", "Selective prediction",
        "External validation", "AI-tool disclosure", "Appendix B",
    ]
    missing = [term for term in required if term not in extracted]
    if missing:
        raise RuntimeError(f"PDF text verification failed: {missing}")
    print(f"WROTE {OUTPUT.relative_to(ROOT)} ({pages} pages, {OUTPUT.stat().st_size} bytes)")
    return pages


if __name__ == "__main__":
    build()
