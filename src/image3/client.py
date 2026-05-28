"""ComfyUI REST API client."""
import json
import time
import uuid
import requests
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


class ComfyClient:
    """Minimal ComfyUI API client for workflow submission and output download."""

    def __init__(self, base_url: str = "http://127.0.0.1:8188"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        # Don't proxy localhost
        self.session.trust_env = False

    def _url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    def health(self) -> bool:
        """Check if ComfyUI server is reachable."""
        try:
            r = self.session.get(self._url("/system_stats"), timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def queue_prompt(self, workflow: dict) -> str:
        """Submit a workflow and return prompt_id."""
        payload = {"prompt": workflow, "client_id": str(uuid.uuid4())}
        r = self.session.post(self._url("/prompt"), json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["prompt_id"]

    def wait_for_completion(self, prompt_id: str, poll_interval: float = 1.0, timeout: float = 600) -> dict:
        """Poll until the prompt completes, return history entry."""
        start = time.time()
        while time.time() - start < timeout:
            r = self.session.get(self._url("/history"), timeout=10)
            r.raise_for_status()
            history = r.json()
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(poll_interval)
        raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")

    def download_outputs(self, history_entry: dict, output_dir: Path) -> list[Path]:
        """Download all outputs from a completed prompt. Returns list of file paths."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []

        for node_id, node_output in history_entry.get("outputs", {}).items():
            for item in node_output.get("images", []):
                filename = item["filename"]
                subfolder = item.get("subfolder", "")
                params = {"filename": filename, "subfolder": subfolder, "type": "output"}
                r = self.session.get(self._url("/view"), params=params, timeout=60)
                r.raise_for_status()

                dest = output_dir / filename
                dest.write_bytes(r.content)
                outputs.append(dest)

        return outputs

    def upload_image(self, image_path: Path, overwrite: bool = True) -> str:
        """Upload an image to ComfyUI input directory. Returns the server-side filename."""
        with open(image_path, "rb") as f:
            files = {"image": (image_path.name, f)}
            data = {"type": "input", "overwrite": str(overwrite).lower()}
            r = self.session.post(self._url("/upload/image"), files=files, data=data, timeout=30)
        r.raise_for_status()
        return r.json()["name"]

    def inject_image(self, workflow: dict, param_name: str, server_filename: str) -> dict:
        """
        Inject an uploaded image filename into a workflow node input.
        Finds the first node with LoadImage and sets its 'image' widget to server_filename.
        """
        import copy
        wf = copy.deepcopy(workflow)
        found = False
        for node_id, node in wf.items():
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = server_filename
                found = True
                break
        if not found:
            raise ValueError("No LoadImage node found in workflow")
        return wf

    def close(self):
        self.session.close()
