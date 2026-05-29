"""Add watermark to zodiac ink images + generate eye-catching cover."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math

# --- Config ---
SRC_DIR = Path(__file__).parent.parent / "output" / "zodiac_ink"
DST_DIR = SRC_DIR / "watermarked"
DST_DIR.mkdir(exist_ok=True)

TEXT = "复旦杰伦@小红书"
FONT_SIZE = 32

# Find Chinese font
font = None
for fp in [
    Path("/usr/share/fonts/google-droid/DroidSansFallback.ttf"),
    Path.home() / ".local/share/fonts/NotoSansSC-Bold.otf",
    Path.home() / ".local/share/fonts/NotoSansSC-Regular.otf",
]:
    if fp.exists():
        font = ImageFont.truetype(str(fp), size=FONT_SIZE)
        break
if font is None:
    font = ImageFont.load_default()


def add_watermark(img_path: Path, dst_path: Path):
    """Add semi-transparent tiled watermark."""
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bbox = draw.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Tiled diagonal watermark for better protection
    spacing_x = tw + 120
    spacing_y = th + 180

    for yi in range(-h, h * 2, spacing_y):
        for xi in range(-w, w * 2, spacing_x):
            # Create rotated text on a temp image
            txt_img = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((10, 10), TEXT, font=font, fill=(255, 255, 255, 45))
            rotated = txt_img.rotate(30, expand=True, resample=Image.BICUBIC)
            # Paste onto overlay
            paste_x = xi - rotated.width // 2
            paste_y = yi - rotated.height // 2
            if -rotated.width < paste_x < w and -rotated.height < paste_y < h:
                overlay.paste(rotated, (paste_x, paste_y), rotated)

    # Also add a clearer watermark in bottom-right corner
    corner_font = ImageFont.truetype(str(fp), size=28) if font != ImageFont.load_default() else font
    bbox2 = draw.textbbox((0, 0), TEXT, font=corner_font)
    tw2, th2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    margin = 20
    draw.text((w - tw2 - margin, h - th2 - margin), TEXT, font=corner_font, fill=(255, 255, 255, 140))

    watermarked = Image.alpha_composite(img, overlay).convert("RGB")
    watermarked.save(str(dst_path), "PNG")
    return dst_path


def create_cover():
    """Create 3x4 grid cover with all 12 zodiac animals — eye-catching for Xiaohongshu."""
    imgs = sorted(SRC_DIR.glob("zodiac_*.png"))
    if len(imgs) < 12:
        print(f"  WARNING: only {len(imgs)} images found, need 12")
        return

    # Cover size: 1080x1440 (3:4 for Xiaohongshu)
    cover_w, cover_h = 1080, 1440
    cols, rows = 4, 3
    cell_w = cover_w // cols
    cell_h = cover_h // rows

    # Background
    cover = Image.new("RGB", (cover_w, cover_h), (245, 240, 230))  # Warm rice paper color

    # Place images in grid
    for idx, img_path in enumerate(imgs[:12]):
        row = idx // cols
        col = idx % cols
        img = Image.open(img_path).convert("RGB")

        # Crop to fill cell
        img_ratio = img.width / img.height
        cell_ratio = cell_w / cell_h
        if img_ratio > cell_ratio:
            new_h = img.height
            new_w = int(new_h * cell_ratio)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, new_h))
        else:
            new_w = img.width
            new_h = int(new_w / cell_ratio)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, new_w, top + new_h))

        img = img.resize((cell_w, cell_h), Image.LANCZOS)
        cover.paste(img, (col * cell_w, row * cell_h))

    # Add title overlay band
    overlay = Image.new("RGBA", (cover_w, cover_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Semi-transparent banner at top
    banner_h = 160
    draw.rectangle([(0, 0), (cover_w, banner_h)], fill=(20, 20, 20, 180))

    # Title text
    title_font_size = 72
    title_font = None
    for fp_path in [
        Path("/usr/share/fonts/google-droid/DroidSansFallback.ttf"),
        Path.home() / ".local/share/fonts/NotoSansSC-Bold.otf",
    ]:
        if fp_path.exists():
            title_font = ImageFont.truetype(str(fp_path), size=title_font_size)
            break
    if title_font is None:
        title_font = font

    title = "水墨十二生肖"
    bbox_t = draw.textbbox((0, 0), title, font=title_font)
    tw_t = bbox_t[2] - bbox_t[0]
    draw.text(((cover_w - tw_t) // 2, 25), title, font=title_font, fill=(255, 255, 255, 255))

    # Subtitle
    sub_font = ImageFont.truetype(str(Path("/usr/share/fonts/google-droid/DroidSansFallback.ttf")), size=32)
    subtitle = "AI水墨画 × 国风头像 | 找找你的本命"
    bbox_s = draw.textbbox((0, 0), subtitle, font=sub_font)
    tw_s = bbox_s[2] - bbox_s[0]
    draw.text(((cover_w - tw_s) // 2, 110), subtitle, font=sub_font, fill=(255, 220, 150, 230))

    # Bottom banner
    draw.rectangle([(0, cover_h - 80), (cover_w, cover_h)], fill=(20, 20, 20, 160))
    bottom_text = "12张高清 · 鼠牛虎兔龙蛇马羊猴鸡狗猪"
    bbox_b = draw.textbbox((0, 0), bottom_text, font=sub_font)
    tw_b = bbox_b[2] - bbox_b[0]
    draw.text(((cover_w - tw_b) // 2, cover_h - 65), bottom_text, font=sub_font, fill=(255, 255, 255, 220))

    # Composite
    cover_rgba = cover.convert("RGBA")
    final = Image.alpha_composite(cover_rgba, overlay).convert("RGB")

    cover_path = SRC_DIR / "cover_zodiac.png"
    final.save(str(cover_path), "PNG", quality=95)
    print(f"  Cover → {cover_path} ({cover_path.stat().st_size / 1024:.0f}KB)")
    return cover_path


if __name__ == "__main__":
    # 1. Watermark all images
    originals = sorted([f for f in SRC_DIR.glob("zodiac_*.png") if "cover" not in f.name])
    print(f"=== Adding watermarks to {len(originals)} images ===")
    for img_path in originals:
        out = add_watermark(img_path, DST_DIR / img_path.name)
        print(f"  {img_path.name} → watermarked/")

    print(f"\n=== Creating cover ===")
    create_cover()
    print("\nDone!")
