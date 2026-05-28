#!/usr/bin/env python3
"""Batch generate Xiaohongshu content — runs a workflow N times with prompt variety."""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description="Batch generate Xiaohongshu images")
    parser.add_argument("--theme", required=True, help="Prompt theme (from xiaohongshu/ category)")
    parser.add_argument("--count", type=int, default=12, help="Number of images")
    parser.add_argument("--workflow", default=str(SCRIPT_DIR / "workflows" / "txt2img.json"),
                        help="Workflow JSON")
    parser.add_argument("--output-dir", default="./output/xhs", help="Output directory")
    parser.add_argument("--host", default="http://127.0.0.1:8188", help="ComfyUI server URL")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(SCRIPT_DIR / "generate.py"),
        "--workflow", args.workflow,
        "--host", args.host,
        "--output-dir", str(output_dir),
        "--count", str(args.count),
        "--category", "xiaohongshu",
        "--prompt-name", args.theme,
        "--seed", "-1",
    ]

    print(f"Batch: {args.count} images, theme='{args.theme}'")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
