"""
PDF Processing Utility
Handles page-combining, splitting, merging, compression, and watermarking.

combine_pages uses pypdfium2 for rasterisation — zero poppler/system dependency.
"""

import os
import math
import uuid
from typing import List

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas as rl_canvas

from config import TEMP_DIR, RENDER_DPI

os.makedirs(TEMP_DIR, exist_ok=True)


def _tmp(suffix=".pdf") -> str:
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{suffix}")


# ─────────────────────────────────────────
# Core: Combine N pages into one sheet
# Pure Python — no poppler required.
# Uses pypdfium2 to rasterise pages.
# ─────────────────────────────────────────

def combine_pages(input_path: str, pages_per_sheet: int) -> str:
    """
    Render `pages_per_sheet` original pages onto a single A4 (or A4-landscape)
    output page using pypdfium2 (no poppler needed). Returns output PDF path.
    """
    try:
        import pypdfium2 as pdfium
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "pypdfium2 or Pillow not installed. Run: pip install pypdfium2 Pillow"
        )

    # Rasterise every page with pypdfium2
    doc    = pdfium.PdfDocument(input_path)
    total  = len(doc)
    scale  = RENDER_DPI / 72  # 72 pt = 1 inch baseline

    images: List[Image.Image] = []
    for i in range(total):
        page   = doc[i]
        bitmap = page.render(scale=scale, rotation=0)
        pil_img = bitmap.to_pil()
        images.append(pil_img.convert("RGB"))
    doc.close()

    # Grid layout
    cols, rows = _grid(pages_per_sheet)

    # Orientation: landscape when wider grid
    if cols > rows:
        page_w, page_h = landscape(A4)
    else:
        page_w, page_h = A4

    cell_w = page_w / cols
    cell_h = page_h / rows

    output_path = _tmp()
    c = rl_canvas.Canvas(output_path, pagesize=(page_w, page_h))

    page_idx = 0
    while page_idx < total:
        # White background
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        for slot in range(pages_per_sheet):
            if page_idx >= total:
                break
            img   = images[page_idx]
            page_idx += 1

            row = slot // cols
            col = slot % cols

            img_w, img_h = img.size
            scale_fit    = min(cell_w / img_w, cell_h / img_h) * 0.96  # 4% margin

            draw_w = img_w * scale_fit
            draw_h = img_h * scale_fit

            x = col * cell_w + (cell_w - draw_w) / 2
            y = page_h - (row + 1) * cell_h + (cell_h - draw_h) / 2

            tmp_img = _tmp(".jpg")
            img.save(tmp_img, "JPEG", quality=93)
            c.drawImage(tmp_img, x, y, draw_w, draw_h)
            os.remove(tmp_img)

        c.showPage()

    c.save()
    return output_path


def _grid(n: int):
    """Return (cols, rows) for n pages per sheet."""
    layouts = {
        1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2),
        6: (3, 2), 8: (4, 2), 9: (3, 3), 12: (4, 3),
        16: (4, 4),
    }
    if n in layouts:
        return layouts[n]
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return cols, rows


# ─────────────────────────────────────────
# Split: one page per file → zip
# ─────────────────────────────────────────

def split_pdf(input_path: str) -> List[str]:
    """Split every page into its own PDF. Returns list of paths."""
    reader = PdfReader(input_path)
    paths  = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out = _tmp()
        with open(out, "wb") as f:
            writer.write(f)
        paths.append(out)
    return paths


# ─────────────────────────────────────────
# Merge: list of PDFs → single PDF
# ─────────────────────────────────────────

def merge_pdfs(paths: List[str]) -> str:
    """Merge multiple PDFs into one. Returns output path."""
    writer = PdfWriter()
    for p in paths:
        reader = PdfReader(p)
        for page in reader.pages:
            writer.add_page(page)
    out = _tmp()
    with open(out, "wb") as f:
        writer.write(f)
    return out


# ─────────────────────────────────────────
# Compress: reduce file size
# ─────────────────────────────────────────

def compress_pdf(input_path: str) -> str:
    """Lossless compress via pypdf page rewrite."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    out = _tmp()
    with open(out, "wb") as f:
        writer.write(f)
    return out


# ─────────────────────────────────────────
# Rotate all pages
# ─────────────────────────────────────────

def rotate_pdf(input_path: str, degrees: int) -> str:
    """Rotate all pages by `degrees` (90, 180, 270)."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)
    out = _tmp()
    with open(out, "wb") as f:
        writer.write(f)
    return out


# ─────────────────────────────────────────
# Extract page range
# ─────────────────────────────────────────

def extract_pages(input_path: str, start: int, end: int) -> str:
    """Extract pages start..end (1-indexed inclusive)."""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total  = len(reader.pages)
    start  = max(1, start)
    end    = min(total, end)
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])
    out = _tmp()
    with open(out, "wb") as f:
        writer.write(f)
    return out


# ─────────────────────────────────────────
# Add text watermark
# ─────────────────────────────────────────

def watermark_pdf(input_path: str, text: str) -> str:
    """Stamp a diagonal text watermark on every page."""
    from reportlab.lib.colors import Color

    reader   = PdfReader(input_path)
    out_path = _tmp()

    c = rl_canvas.Canvas(out_path)
    for page in reader.pages:
        box    = page.mediabox
        pw, ph = float(box.width), float(box.height)
        c.setPageSize((pw, ph))
        c.saveState()
        c.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.25))
        c.setFont("Helvetica-Bold", min(pw, ph) // 12)
        c.translate(pw / 2, ph / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.showPage()
    c.save()

    # Merge watermark over original pages
    wm_reader = PdfReader(out_path)
    writer    = PdfWriter()
    for orig_page, wm_page in zip(reader.pages, wm_reader.pages):
        orig_page.merge_page(wm_page)
        writer.add_page(orig_page)

    final = _tmp()
    with open(final, "wb") as f:
        writer.write(f)
    os.remove(out_path)
    return final


# ─────────────────────────────────────────
# Get page count
# ─────────────────────────────────────────

def page_count(input_path: str) -> int:
    return len(PdfReader(input_path).pages)


# ─────────────────────────────────────────
# Cleanup helper
# ─────────────────────────────────────────

def cleanup(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
