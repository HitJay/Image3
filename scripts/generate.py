#!/usr/bin/env python3
"""Generate images via ComfyUI — the main entry point for all generation tasks."""
import argparse
import json
import random
import sys
from pathlib import Path

# Add src to path when run as script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image3.client import ComfyClient
from image3.prompts import PromptLibrary, BUILTIN_WALLPAPERS, BUILTIN_CREATIVE, BUILTIN_XHS


def load_workflow(path: str) -> dict:
    """Load a ComfyUI workflow JSON in API format."""
    with open(path) as f:
        wf = json.load(f)
    # Detect editor format and warn
    if "nodes" in wf and "links" in wf:
        print("WARNING: Workflow is in editor format. Export as API format from ComfyUI.")
        print("  In ComfyUI: Workflow → Export (API)")
        sys.exit(1)
    return wf


def inject_prompt(workflow: dict, prompt: str, negative: str = "") -> dict:
    """Inject a text prompt into a workflow — finds CLIPTextEncode nodes."""
    import copy
    wf = copy.deepcopy(workflow)
    pos_found = False
    neg_found = False
    for node in wf.values():
        if node.get("class_type") == "CLIPTextEncode":
            text = node.get("_meta", {}).get("title", "").lower()
            if "negative" in text:
                if not neg_found and negative:
                    node["inputs"]["text"] = negative
                    neg_found = True
            else:
                if not pos_found:
                    node["inputs"]["text"] = prompt
                    pos_found = True
    if not pos_found:
        print("WARNING: No CLIPTextEncode node found for positive prompt")
    return wf


def inject_seed(workflow: dict, seed: int = -1) -> dict:
    """Inject seed into KSampler nodes. -1 = random."""
    import copy
    wf = copy.deepcopy(workflow)
    if seed < 0:
        seed = random.randint(0, 2**31 - 1)
    for node in wf.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = seed
    print(f"  seed: {seed}")
    return wf


def main():
    parser = argparse.ArgumentParser(description="Generate images via ComfyUI")
    parser.add_argument("--workflow", required=True, help="ComfyUI workflow JSON (API format)")
    parser.add_argument("--host", default="http://127.0.0.1:8188", help="ComfyUI server URL")
    parser.add_argument("--prompt", help="Text prompt (overrides workflow default)")
    parser.add_argument("--negative", default="", help="Negative prompt")
    parser.add_argument("--category", choices=["wallpapers", "creative", "xiaohongshu"], help="Prompt category")
    parser.add_argument("--prompt-name", help="Specific prompt template file (without .txt)")
    parser.add_argument("--random-prompt", action="store_true", help="Pick a random prompt from category")
    parser.add_argument("--input-image", help="Input image for img2img workflows")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--count", type=int, default=1, help="Images to generate")
    parser.add_argument("--seed", type=int, default=-1, help="Seed (-1 = random per image)")
    parser.add_argument("--timeout", type=int, default=600, help="Max seconds per image")
    args = parser.parse_args()

    # Resolve prompt
    if args.prompt:
        prompt = args.prompt
    elif args.category and args.prompt_name:
        lib = PromptLibrary()
        prompt = lib.load(args.category, args.prompt_name)
    elif args.category and args.random_prompt:
        lib = PromptLibrary()
        name, prompt = lib.random(args.category)
        print(f"  random prompt [{args.category}]: {name}")
    else:
        prompt = None  # use workflow default

    if prompt:
        print(f"  prompt: {prompt[:80]}...")

    # Load workflow
    wf = load_workflow(args.workflow)
    if prompt:
        wf = inject_prompt(wf, prompt, args.negative)

    # Connect to ComfyUI
    client = ComfyClient(args.host)
    if not client.health():
        print(f"ERROR: ComfyUI server not reachable at {args.host}")
        print("Start it with: comfy launch --background")
        sys.exit(1)
    print(f"  server: OK ({args.host})")

    # Upload input image if provided
    if args.input_image:
        img_path = Path(args.input_image)
        if not img_path.exists():
            print(f"ERROR: Input image not found: {args.input_image}")
            sys.exit(1)
        print(f"  uploading: {img_path.name}")
        server_name = client.upload_image(img_path)
        wf = client.inject_image(wf, "image", server_name)

    # Generate
    output_dir = Path(args.output_dir)
    for i in range(args.count):
        wf_copy = inject_seed(wf, args.seed if args.seed >= 0 else -1)
        label = f"[{i+1}/{args.count}]" if args.count > 1 else ""
        print(f"  submitting {label}...")
        prompt_id = client.queue_prompt(wf_copy)
        print(f"    prompt_id: {prompt_id}")
        print(f"    waiting (timeout={args.timeout}s)...")
        history = client.wait_for_completion(prompt_id, timeout=args.timeout)
        files = client.download_outputs(history, output_dir)
        for f in files:
            print(f"    saved: {f}")

    client.close()
    print("Done.")

if __name__ == "__main__":
    main()
