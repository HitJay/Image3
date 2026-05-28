"""Remote API client for image generation services (MatPool, OpenAI-compatible, etc.)."""
import base64
import json
import re
import time
import requests
from pathlib import Path
from typing import Optional


class ImageAPIClient:
    """Generic client for image generation APIs (OpenAI-compatible format).

    Handles MatPool quirks:
    - Some models return 500 with image URLs buried in error JSON (litellm bug)
    - Nano-Banana-Spot returns proper 200 with data[].url
    """

    def __init__(self, base_url: str, api_key: str, model: str = "Nano-Banana-Spot"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.session = requests.Session()
        # Don't proxy API calls (MatPool doesn't need proxy from China)
        self.session.trust_env = False

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        seed: int = -1,
        cfg_scale: float = 7.0,
        input_image: Optional[Path] = None,
        strength: float = 0.6,
    ) -> dict:
        """Submit a generation request. Returns API response dict with at least {'data': [{'url': ...}]}.

        For img2img, pass input_image path.
        Handles MatPool's litellm 500 wrapper by extracting image URLs from error bodies.
        """
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": f"{width}x{height}",
        }

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed >= 0:
            payload["seed"] = seed
        if steps:
            payload["steps"] = steps

        # img2img mode
        if input_image:
            image_bytes = Path(input_image).read_bytes()
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            payload["image"] = b64
            payload["strength"] = strength

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        r = self.session.post(
            f"{self.base_url}/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=300,
        )

        # MatPool workaround: some models return 500 but image URLs are in the error body
        if r.status_code >= 400:
            return self._extract_urls_from_error(r)

        r.raise_for_status()
        return r.json()

    def _extract_urls_from_error(self, r: requests.Response) -> dict:
        """Extract image URLs from MatPool error responses (litellm bug workaround).

        MatPool's litellm layer sometimes wraps valid image responses in 500 errors.
        We regex-extract the actual image URLs from the raw error JSON.
        """
        try:
            body = r.json()
        except json.JSONDecodeError:
            r.raise_for_status()
            return {}  # unreachable

        raw = json.dumps(body)
        urls = re.findall(r'https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)[^\s"\'<>]*', raw)

        if urls:
            # Filter to MatPool CDN URLs
            image_urls = [u for u in urls if "sydney-ai.com" in u or "oss" in u]
            if not image_urls:
                image_urls = urls  # fallback to any image URL
            return {"data": [{"url": u} for u in image_urls]}

        # No URLs found — raise the original error
        r.raise_for_status()
        return {}  # unreachable, satisfies type checker

    def save_outputs(self, response: dict, output_dir: Path, prefix: str = "img") -> list[Path]:
        """Parse API response and save images. Returns list of saved file paths."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        saved = []

        data = response.get("data", [])
        for i, item in enumerate(data):
            b64_data = item.get("b64_json")
            url = item.get("url")

            ts = int(time.time())
            if b64_data:
                dest = output_dir / f"{prefix}_{ts}_{i:03d}.png"
                dest.write_bytes(base64.b64decode(b64_data))
                saved.append(dest)
            elif url:
                ext = Path(url.split("?")[0]).suffix or ".png"
                dest = output_dir / f"{prefix}_{ts}_{i:03d}{ext}"
                dl = requests.get(url, timeout=60)
                dl.raise_for_status()
                dest.write_bytes(dl.content)
                saved.append(dest)

        return saved

    def close(self):
        self.session.close()


# Known provider presets
PROVIDERS = {
    "matpool": {
        "base_url": "https://token.matpool.com",
        "models": [
            "Nano-Banana-Spot",       # 推荐 — 稳定出图，兼容性好
            "GPT-Image-2",            # 质量高但有 litellm 解析 bug（图能出但报 500）
            "stable-diffusion-3.5-large",
            "flux-1.1-pro",
        ],
        "note": "矩池云 — 需要 API Key",
    },
    "openai": {
        "base_url": "https://api.openai.com",
        "models": ["dall-e-3", "dall-e-2"],
        "note": "OpenAI — 按张计费",
    },
}
