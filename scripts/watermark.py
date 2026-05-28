"""Add '复旦杰伦@小红书' watermark to original cat images."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

src_dir = Path("/mnt/d/vscode/Image3/output/ukiyo_cats")
dst_dir = src_dir / "watermarked"
dst_dir.mkdir(exist_ok=True)

originals = sorted([f for f in src_dir.glob("ukiyo_*.png")])
text = "复旦杰伦@小红书"

# Chinese font
font = None
for fp in [
    Path.home() / ".local/share/fonts/NotoSansSC-Regular.otf",
    Path.home() / ".local/share/fonts/NotoSansSC-Bold.otf",
    Path("/mnt/c/Windows/Fonts/msyh.ttc"),
]:
    if fp.exists():
        font = ImageFont.truetype(str(fp), size=28)
        break
if font is None:
    font = ImageFont.load_default()

for img_path in originals:
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    margin = 24
    x, y = w - tw - margin, h - th - margin

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 100))

    watermarked = Image.alpha_composite(img, overlay).convert("RGB")
    out_path = dst_dir / img_path.name
    watermarked.save(str(out_path), "PNG")
    print(f"  {img_path.name} → watermarked/{img_path.name} ({out_path.stat().st_size / 1024:.0f}KB)")

print(f"\nDone! {len(originals)} images → {dst_dir}")
