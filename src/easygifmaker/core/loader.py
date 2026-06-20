# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions for loading PNG images"""

from pathlib import Path
from PIL import Image


def load_image(path: str | Path) -> Image.Image:
    """Load a single PNG and convert to RGBA"""
    image = Image.open(path)
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return image

def load_images(paths: list[str | Path]) -> list[Image.Image]:
    """Load multiple PNGs as RGBA images"""
    return [load_image(path) for path in paths]