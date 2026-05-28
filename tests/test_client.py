"""Tests for ComfyClient."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image3.client import ComfyClient


def test_client_default_url():
    client = ComfyClient()
    assert client.base_url == "http://127.0.0.1:8188"
    client.close()


def test_client_custom_url():
    client = ComfyClient("http://localhost:8190")
    assert client.base_url == "http://localhost:8190"
    client.close()


def test_client_url_trailing_slash():
    client = ComfyClient("http://127.0.0.1:8188/")
    assert client.base_url == "http://127.0.0.1:8188"
    client.close()


def test_inject_image_no_loadimage():
    client = ComfyClient()
    wf = {"1": {"class_type": "KSampler", "inputs": {}}}
    try:
        client.inject_image(wf, "img", "test.png")
        assert False, "Should raise"
    except ValueError:
        pass
    client.close()
