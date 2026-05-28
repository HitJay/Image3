"""Remote API client for image generation services (MatPool, OpenAI-compatible, etc.)."""
import base64
import time
import requests
from pathlib import Path
from typing import Optional


class ImageAPIClient:
    """Generic client for image generation APIs (OpenAI-compatible format)."""

    def __init__(self, base_url: str, api_key: str, model: str = "GPT-Image-2"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.session = requests.Session()

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
        strength: float = 0.6,  # img2img denoise
    ) -> dict:
        """
        Submit a generation request. Returns API response dict.
        For img2img, pass input_image path.
        """
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": f"{width}x{height}",
        }

        # OpenAI-compatible extra params
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed >= 0:
            payload["seed"] = seed
        if steps:
            payload["steps"] = steps

        # img2img mode — encode input image as base64
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
        r.raise_for_status()
        return r.json()

    def save_outputs(self, response: dict, output_dir: Path, prefix: str = "img") -> list[Path]:
        """
        Parse API response and save images. Handles both base64 data and URLs.
        Returns list of saved file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        saved = []

        data = response.get("data", [])
        for i, item in enumerate(data):
            b64_data = item.get("b64_json")
            url = item.get("url")

            ts = int(time.time())
            if b64_data:
                ext = ".png"  # base64 is usually PNG
                dest = output_dir / f"{prefix}_{ts}_{i:03d}{ext}"
                dest.write_bytes(base64.b64decode(b64_data))
                saved.append(dest)
            elif url:
                ext = Path(url.split("?")[0]).suffix or ".png"
                dest = output_dir / f"{prefix}_{ts}_{i:03d}{ext}"
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                dest.write_bytes(r.content)
                saved.append(dest)

        return saved

    def close(self):
        self.session.close()


# Known provider presets
PROVIDERS = {
    "matpool": {
        "base_url": "https://token.matpool.com",
        "models": ["GPT-Image-2", "stable-diffusion-3.5-large", "flux-1.1-pro"],
        "note": "矩池云 — 需要 API Key",
    },
    "openai": {
        "base_url": "https://api.openai.com",
        "models": ["dall-e-3", "dall-e-2"],
        "note": "OpenAI — 按张计费",
    },
}
