"""CLI entry point for Image3."""
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="image3",
        description="AI Image Generation Workbench powered by ComfyUI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate images")
    gen_parser.add_argument("--workflow", required=True, help="Path to workflow JSON")
    gen_parser.add_argument("--prompt", help="Text prompt")
    gen_parser.add_argument("--category", choices=["wallpapers", "creative", "xiaohongshu"], help="Prompt category")
    gen_parser.add_argument("--prompt-name", help="Specific prompt template name")
    gen_parser.add_argument("--input-image", help="Input image for img2img")
    gen_parser.add_argument("--output-dir", default="./output", help="Output directory")
    gen_parser.add_argument("--host", default="http://127.0.0.1:8188", help="ComfyUI server URL")
    gen_parser.add_argument("--count", type=int, default=1, help="Number of images to generate")
    gen_parser.add_argument("--seed", type=int, default=-1, help="Random seed (-1 for random)")

    # health
    subparsers.add_parser("health", help="Check ComfyUI server status")

    args = parser.parse_args()

    if args.command == "health":
        from image3.client import ComfyClient
        client = ComfyClient(args.host if hasattr(args, "host") else "http://127.0.0.1:8188")
        ok = client.health()
        print(f"ComfyUI @ {client.base_url}: {'HEALTHY' if ok else 'UNREACHABLE'}")
        client.close()
        sys.exit(0 if ok else 1)

    elif args.command == "generate":
        print(f"Not yet implemented. Workflow: {args.workflow}, Prompt: {args.prompt}")
        sys.exit(0)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
