"""Tests for prompt library."""
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image3 import prompts


def test_builtin_wallpapers():
    assert len(prompts.BUILTIN_WALLPAPERS) >= 4
    assert "cyberpunk" in prompts.BUILTIN_WALLPAPERS
    for name, text in prompts.BUILTIN_WALLPAPERS.items():
        assert isinstance(name, str) and len(name) > 0
        assert isinstance(text, str) and len(text) > 20


def test_builtin_creative():
    assert len(prompts.BUILTIN_CREATIVE) >= 4
    assert "cat_astronaut" in prompts.BUILTIN_CREATIVE


def test_builtin_xhs():
    assert len(prompts.BUILTIN_XHS) >= 3
    assert "mood_board" in prompts.BUILTIN_XHS


def test_prompt_library_categories():
    lib = prompts.PromptLibrary(prompts_dir=Path(tempfile.mkdtemp()))
    assert lib.list_categories() == []
    assert lib.list_prompts("nonexistent") == []


def test_prompt_library_random_empty():
    lib = prompts.PromptLibrary(prompts_dir=Path(tempfile.mkdtemp()))
    try:
        lib.random("empty")
        assert False, "Should have raised"
    except ValueError:
        pass
