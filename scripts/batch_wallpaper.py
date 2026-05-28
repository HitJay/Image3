#!/usr/bin/env python3
"""Batch generate wallpaper images via API."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Batch generate wallpapers")
    parser.add_argument("--theme", required=True, help="Prompt theme (wallpapers/ category)")
    parser.add_argument("--count", type=int, default=10, help="Number of wallpapers")
    parser.add_argument("--output-dir", default="./output/wallpapers", help="Output directory")
    parser.add_argument("--provider", default="matpool", help="Generation provider")
    parser.add_argument("--width", type=int, default=1440, help="Width (wallpaper aspect)")
    parser.add_argument("--height", type=int, default=960, help="Height (wallpaper aspect)")
    parser.add_argument("--api-key", help="API key (or IMAGE_API_KEY env)")
    parser.add_argument("--model", help="Model override")
    args = parser.parse_args()

    cmd = [
        sys.executable, str(SCRIPT_DIR / "generate.py"),
        "--provider", args.provider,
        "--category", "wallpapers",
        "--prompt-name", args.theme,
        "--output-dir", str(args.output_dir),
        "--count", str(args.count),
        "--width", str(args.width),
        "--height", str(args.height),
        "--prefix", f"wp_{args.theme}",
        "--seed", "-1",
    ]
    if args.api_key:
        cmd += ["--api-key", args.api_key]
    if args.model:
        cmd += ["--model", args.model]

    print(f"Batch wallpaper: {args.count} images, theme='{args.theme}'")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
