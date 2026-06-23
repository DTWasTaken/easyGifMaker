# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions for exporting frames to GIF."""

from pathlib import Path
from PIL import Image

def save_gif(
    animation: list[tuple[Image.Image, int]],
    output_file_path: Path,
    loop: int = 0,
    ) -> None:
    
    """Save a list of PIL images as an animated GIF."""

    frames = []
    durations = []
    
    for item in animation:
        frame, duration = item
        frames.append(frame)
        durations.append(duration)
       
    first, *rest = frames
    first.save(
        output_file_path,
        save_all=True,
        append_images=rest,
        duration=durations,
        loop=loop,
        disposal=2,
        optimize=True,
    )