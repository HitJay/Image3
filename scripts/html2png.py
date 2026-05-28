"""Convert HTML cards to PNG — weasyprint → PyMuPDF, zero margin, exact crop."""
import fitz
from pathlib import Path
from weasyprint import HTML

cards_dir = Path("/mnt/d/vscode/Image3/output/ukiyo_cats/cards")
html_files = sorted(cards_dir.glob("*.html"))

for hf in html_files:
    name = hf.stem
    pdf_path = cards_dir / f"{name}.pdf"
    png_path = cards_dir / f"{name}.png"

    print(f"  {name} ...", end=" ", flush=True)

    # Inject @page CSS
    html_content = hf.read_text(encoding="utf-8")
    # weasyprint uses 96dpi, so 600px = 450pt, 780px = 585pt
    page_css = """
  @page {
    size: 450pt 585pt;
    margin: 0;
  }"""
    html_content = html_content.replace("</style>", page_css + "\n</style>", 1)

    HTML(string=html_content).write_pdf(str(pdf_path))

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    # Get the actual page rect
    r = page.rect
    print(f"(page {r.width:.0f}x{r.height:.0f}pt)", end=" ", flush=True)

    # Render at 2x, clip to page bounds
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat, clip=r)
    pix.save(str(png_path))
    doc.close()
    pdf_path.unlink()

    size_kb = png_path.stat().st_size / 1024
    print(f"→ {size_kb:.0f}KB")

print(f"\nDone! {len(html_files)} PNGs → {cards_dir}")
