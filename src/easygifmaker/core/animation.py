# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from PIL import Image

from .project import LoadedProject
from .schemas import TimingAnimation
from easygifmaker.exceptions import AnimationError


DEFAULT_FRAME_DURATION = 200

def load_frame(path: Path) -> Image.Image:
    """Load a single PNG and convert to RGBA"""
    
    """
    Should I close files after loading, or keep images open until export? 
    Do I want to call load() or copy() if you instead of open()?
    """
    
    frame = Image.open(path)
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")
         
    return frame


def timing_animation(
    animation: TimingAnimation,
    raw_frames: list[Image.Image]
    ) -> list[(Image.Image, int)]:
    
    # Get pattern, if it's not defined, use default
    pattern = animation.pattern
    if pattern is None:
        pattern = [DEFAULT_FRAME_DURATION]
        
    num_output_frames = max(len(raw_frames), len(pattern))
    
    output = []
        
    # Cycle frames and durations to max(len(frames), len(pattern))
    for i in range(num_output_frames):
        output.append((raw_frames[i % len(raw_frames)], pattern[i % len(pattern)]))
    
    return output

def build_animation(loaded_project: LoadedProject) -> list[(Image.Image, int)]:
    # Error if no frames found
    if len(loaded_project.frames) == 0:
        raise AnimationError(
            f"No frames found in {loaded_project.project.sources.frames}"
            )
    
    # Load images
    raw_frames = []
    frame_dimensions = (None, None)
    for frame in loaded_project.frames:
        raw_frame = load_frame(frame)
        
        # Validate all frames have the same size 
        if frame_dimensions == (None, None):
            frame_dimensions = (raw_frame.height, raw_frame.width)
        elif (raw_frame.height, raw_frame.width) != frame_dimensions:
            raise AnimationError("Frame dimensions do not match")
        raw_frames.append(raw_frame)
          
    
    # Load and validate background if needed
    background_frame = None
    if loaded_project.background:
        background_frame = load_frame(frame)
        
        if (background_frame.height, background_frame.width) != frame_dimensions:
            raise AnimationError(
                "Background frame dimensions do not match rest of frames"
                )
    
    # Animate frames
    animation = loaded_project.project.animation
    match animation.mode:
        case "timing":
            return timing_animation(animation, raw_frames)
        case _:
            raise AnimationError(
                f"Animation type ({animation.mode}) not yetimplemented"
                )
