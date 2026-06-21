# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions for exporting frames to GIF."""

from pathlib import Path
from PIL import Image


def save_gif(
    frames: list[Image.Image],
    output_path: str | Path,
    pattern: list[str],
    loop: int = 0,
    ) -> None:
    
    """Save a list of PIL images as an animated GIF."""
    if not frames:
        raise ValueError("No frames to export")
   
    if len(pattern) > len(frames):
        frames = [frames[i % len(frames)] for i in range(len(pattern))]
        
    durations = []
        
    for i in range(len(frames)):
        durations.append(int(pattern[i % len(pattern)]))
       
    first, *rest = frames
    first.save(
        output_path,
        save_all=True,
        append_images=rest,
        duration=durations,
        loop=loop,
        disposal=2,
        optimize=True,
    )