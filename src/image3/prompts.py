"""Prompt template management."""
import random
from pathlib import Path
from typing import Optional


class PromptLibrary:
    """Load and manage prompt templates from the prompts/ directory."""

    def __init__(self, prompts_dir: Optional[Path] = None):
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.root = Path(prompts_dir)

    def list_categories(self) -> list[str]:
        """List available prompt categories (subdirectories)."""
        if not self.root.exists():
            return []
        return [d.name for d in self.root.iterdir() if d.is_dir()]

    def list_prompts(self, category: str) -> list[Path]:
        """List all .txt prompt files in a category."""
        cat_dir = self.root / category
        if not cat_dir.exists():
            return []
        return sorted(cat_dir.glob("*.txt"))

    def load(self, category: str, name: str) -> str:
        """Load a specific prompt template."""
        path = self.root / category / name
        if not path.suffix:
            path = path.with_suffix(".txt")
        return path.read_text(encoding="utf-8").strip()

    def random(self, category: str) -> tuple[str, str]:
        """Pick a random prompt from the category. Returns (name, prompt_text)."""
        prompts = self.list_prompts(category)
        if not prompts:
            raise ValueError(f"No prompts found in category '{category}'")
        chosen = random.choice(prompts)
        return chosen.stem, self.load(category, chosen.name)


# Built-in minimal prompt templates for bootstrapping
BUILTIN_WALLPAPERS = {
    "cyberpunk": "cyberpunk city at night, neon lights, rain, reflections, ultra detailed, 8K wallpaper",
    "nature": "serene mountain lake at sunrise, misty atmosphere, photorealistic, 8K wallpaper",
    "abstract": "flowing geometric shapes, gradient colors, minimal design, clean, modern wallpaper",
    "space": "nebula galaxy, stars, cosmic dust, vibrant colors, ethereal, 8K wallpaper",
    "japan": "traditional japanese garden, cherry blossoms, pagoda, peaceful, artistic, wallpaper",
}

BUILTIN_CREATIVE = {
    "cat_astronaut": "a cute cat wearing an astronaut helmet floating in space, digital art, vibrant",
    "pixel_world": "isometric pixel art fantasy village, cozy, detailed, game art style",
    "fruit_animal": "a fox made entirely of autumn leaves and berries, magical, artistic photography",
    "mini_world": "tiny people living inside a glass terrarium, macro photography, whimsical",
    "vaporwave": "vaporwave aesthetic marble statue with neon sunglasses, retro synthwave, purple and pink",
}

BUILTIN_XHS = {
    "mood_board": "aesthetic mood board, warm tones, cozy vibes, film grain, pinterest style, 4:3",
    "flat_lay": "flat lay creative workspace, art supplies, plants, coffee, natural light, lifestyle",
    "color_study": "color palette study, monochromatic composition, artistic, elegant, minimal",
    "texture": "close-up beautiful paper textures, fabric folds, organic shapes, soft lighting",
}
