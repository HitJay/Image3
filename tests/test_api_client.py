"""Tests for ImageAPIClient."""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image3.api_client import ImageAPIClient, PROVIDERS


def test_client_init():
    client = ImageAPIClient("https://token.matpool.com", "key123")
    assert client.base_url == "https://token.matpool.com"
    assert client.api_key == "key123"
    assert client.model == "GPT-Image-2"
    client.close()


def test_client_custom_model():
    client = ImageAPIClient("https://api.example.com", "key", model="flux-1.1-pro")
    assert client.model == "flux-1.1-pro"
    client.close()


def test_providers_have_matpool():
    assert "matpool" in PROVIDERS
    assert "base_url" in PROVIDERS["matpool"]
    assert "models" in PROVIDERS["matpool"]
    assert len(PROVIDERS["matpool"]["models"]) >= 1


def test_save_outputs_b64():
    import base64, tempfile
    client = ImageAPIClient("http://localhost", "key")
    resp = {"data": [{"b64_json": base64.b64encode(b"fake-png-data").decode()}]}
    with tempfile.TemporaryDirectory() as td:
        files = client.save_outputs(resp, Path(td))
        assert len(files) == 1
        assert files[0].suffix == ".png"
        assert files[0].read_bytes() == b"fake-png-data"
    client.close()


def test_save_outputs_url():
    import tempfile
    client = ImageAPIClient("http://localhost", "key")
    resp = {"data": [{"url": "https://cdn.example.com/img.jpg"}]}
    with tempfile.TemporaryDirectory() as td, \
         patch("requests.get") as mock_get:
        mock_get.return_value.content = b"fake-jpg"
        mock_get.return_value.raise_for_status = Mock()
        files = client.save_outputs(resp, Path(td))
        assert len(files) == 1
        assert files[0].suffix == ".jpg"
    client.close()


def test_generate_payload():
    """Verify generate() constructs correct payload."""
    client = ImageAPIClient("http://localhost", "key", model="flux")
    with patch.object(client.session, "post") as mock_post:
        mock_post.return_value.json.return_value = {"data": []}
        mock_post.return_value.raise_for_status = Mock()
        client.generate("test prompt", negative_prompt="ugly", seed=42, steps=20)
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["model"] == "flux"
        assert payload["prompt"] == "test prompt"
        assert payload["negative_prompt"] == "ugly"
        assert payload["seed"] == 42
        assert payload["steps"] == 20
    client.close()
