# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Functions for loading PNG images"""

from pathlib import Path
from PIL import Image
from natsort import natsorted


def load_frame(path: Path) -> Image.Image:
    """Load a single PNG and convert to RGBA"""
    if not path.is_file():
        raise ValueError("Input is not a file")
   
    frame = Image.open(path)
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")
         
    return frame

def load_frames(frames_dir: Path) -> list[Image.Image]:
    """Load multiple PNGs as RGBA images"""
    frames = []
    if not frames_dir.is_dir():
        raise ValueError("Input is not a directory")
    
    pngs = natsorted(frames_dir.glob("*.png"))
    
    for png in pngs:
        frames.append(load_frame(png))
            
    return frames