#!/usr/bin/env python3
"""Batch generate Xiaohongshu content via API."""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Batch generate Xiaohongshu images")
    parser.add_argument("--theme", required=True, help="Prompt theme (xiaohongshu/ category)")
    parser.add_argument("--count", type=int, default=12, help="Number of images")
    parser.add_argument("--output-dir", default="./output/xhs", help="Output directory")
    parser.add_argument("--provider", default="matpool", help="Generation provider")
    parser.add_argument("--width", type=int, default=768, help="Width (3:4 portrait)")
    parser.add_argument("--height", type=int, default=1024, help="Height (3:4 portrait)")
    parser.add_argument("--api-key", help="API key (or IMAGE_API_KEY env)")
    parser.add_argument("--model", help="Model override")
    args = parser.parse_args()

    cmd = [
        sys.executable, str(SCRIPT_DIR / "generate.py"),
        "--provider", args.provider,
        "--category", "xiaohongshu",
        "--prompt-name", args.theme,
        "--output-dir", str(args.output_dir),
        "--count", str(args.count),
        "--width", str(args.width),
        "--height", str(args.height),
        "--prefix", f"xhs_{args.theme}",
        "--seed", "-1",
    ]
    if args.api_key:
        cmd += ["--api-key", args.api_key]
    if args.model:
        cmd += ["--model", args.model]

    print(f"Batch XHS: {args.count} images, theme='{args.theme}', {args.width}x{args.height}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
