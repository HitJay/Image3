#!/usr/bin/env python3
"""Generate images — supports both API (MatPool/OpenAI) and local ComfyUI.

API mode (default, no GPU needed):
  python3 scripts/generate.py --provider matpool --prompt "一只猫在太空站"

ComfyUI mode (local GPU):
  python3 scripts/generate.py --provider comfyui --workflow workflows/txt2img.json --prompt "..."
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image3.prompts import PromptLibrary


def resolve_prompt(args) -> str:
    """Resolve prompt from --prompt, --category/--prompt-name, or --random-prompt."""
    if args.prompt:
        return args.prompt
    if args.category and args.prompt_name:
        lib = PromptLibrary()
        return lib.load(args.category, args.prompt_name)
    if args.category and args.random_prompt:
        lib = PromptLibrary()
        name, text = lib.random(args.category)
        print(f"  [random] {args.category}/{name}")
        return text
    print("ERROR: --prompt or --category required")
    sys.exit(1)


def run_api(args, prompt: str):
    """Generate via remote API (MatPool / OpenAI-compatible)."""
    from image3.api_client import ImageAPIClient, PROVIDERS

    provider = PROVIDERS.get(args.provider) or {}
    base_url = args.api_base or provider.get("base_url", "")
    api_key = args.api_key or os.environ.get("IMAGE_API_KEY", "")

    if not base_url:
        print("ERROR: --api-base required (or use known provider: matpool)")
        sys.exit(1)
    if not api_key:
        print("ERROR: IMAGE_API_KEY env or --api-key required")
        sys.exit(1)

    model = args.model or provider.get("models", [args.model])[0]
    print(f"  provider: {args.provider}")
    print(f"  model: {model}")
    print(f"  prompt: {prompt[:80]}...")

    client = ImageAPIClient(base_url, api_key, model)

    input_image = Path(args.input_image) if args.input_image else None
    for i in range(args.count):
        label = f"[{i+1}/{args.count}]" if args.count > 1 else ""
        print(f"  generating {label}...")
        resp = client.generate(
            prompt=prompt,
            negative_prompt=args.negative or "",
            width=args.width,
            height=args.height,
            steps=args.steps,
            seed=args.seed,
            input_image=input_image,
            strength=args.strength,
        )
        files = client.save_outputs(resp, Path(args.output_dir), prefix=args.prefix)
        for f in files:
            print(f"  -> {f}")

    client.close()
    print("Done.")


def run_comfyui(args, prompt: str):
    """Generate via local ComfyUI."""
    import json
    import random
    import copy

    from image3.client import ComfyClient

    with open(args.workflow) as f:
        wf = json.load(f)

    if "nodes" in wf and "links" in wf:
        print("ERROR: workflow is editor format. Export as API format from ComfyUI.")
        sys.exit(1)

    # Inject prompt
    for node in wf.values():
        if node.get("class_type") == "CLIPTextEncode":
            text = node.get("_meta", {}).get("title", "").lower()
            if "negative" not in text:
                node["inputs"]["text"] = prompt
                break

    client = ComfyClient(args.comfy_host)
    if not client.health():
        print(f"ERROR: ComfyUI not reachable at {args.comfy_host}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    for i in range(args.count):
        wf_copy = copy.deepcopy(wf)
        seed = args.seed if args.seed >= 0 else random.randint(0, 2**31 - 1)
        for node in wf_copy.values():
            if node.get("class_type") == "KSampler":
                node["inputs"]["seed"] = seed
        print(f"  [{i+1}/{args.count}] seed={seed}...")
        prompt_id = client.queue_prompt(wf_copy)
        history = client.wait_for_completion(prompt_id, timeout=args.timeout)
        files = client.download_outputs(history, output_dir)
        for f in files:
            print(f"  -> {f}")

    client.close()
    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Generate images via API or ComfyUI")

    # Provider
    parser.add_argument("--provider", default="matpool",
                        choices=["matpool", "openai", "comfyui", "custom"],
                        help="Generation backend (default: matpool)")

    # Prompt
    parser.add_argument("--prompt", help="Text prompt")
    parser.add_argument("--negative", default="", help="Negative prompt")
    parser.add_argument("--category", choices=["wallpapers", "creative", "xiaohongshu"],
                        help="Prompt category from prompts/")
    parser.add_argument("--prompt-name", help="Specific prompt template (without .txt)")
    parser.add_argument("--random-prompt", action="store_true", help="Random prompt from category")

    # Output
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--count", type=int, default=1, help="Images to generate")
    parser.add_argument("--prefix", default="img", help="Output filename prefix")

    # Image params
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--steps", type=int, default=30, help="Sampling steps")
    parser.add_argument("--seed", type=int, default=-1, help="Seed (-1 = random)")
    parser.add_argument("--input-image", help="Input image for img2img")
    parser.add_argument("--strength", type=float, default=0.6, help="img2img denoise strength")

    # API options
    parser.add_argument("--api-base", help="API base URL (default: matpool)")
    parser.add_argument("--api-key", help="API key (or set IMAGE_API_KEY env)")
    parser.add_argument("--model", help="Model name (default: provider-specific)")

    # ComfyUI options
    parser.add_argument("--workflow", help="ComfyUI workflow JSON (API format)")
    parser.add_argument("--comfy-host", default="http://127.0.0.1:8188", help="ComfyUI server URL")
    parser.add_argument("--timeout", type=int, default=600, help="Max seconds per image")

    args = parser.parse_args()
    prompt = resolve_prompt(args)

    if args.provider == "comfyui":
        if not args.workflow:
            print("ERROR: --workflow required for ComfyUI mode")
            sys.exit(1)
        run_comfyui(args, prompt)
    else:
        run_api(args, prompt)


if __name__ == "__main__":
    main()
