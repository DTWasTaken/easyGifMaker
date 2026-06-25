# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math

from pathlib import Path
from PIL import Image

from .project import LoadedProject
from .schemas import TimingAnimation, RotateAnimation
from easygifmaker.exceptions import AnimationError


DEFAULT_FRAME_DURATION = 200


def load_frame(path: Path) -> Image.Image:
    """Load a single PNG and convert to RGBA"""
    
    frame = Image.open(path).copy()
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")
         
    return frame


def timing_animation(
    animation: TimingAnimation,
    raw_frames: list[Image.Image],
) -> list[tuple[Image.Image, int]]:
    
    # Get pattern, if it's not defined, use default
    pattern = animation.pattern
    if pattern is None:
        pattern = [DEFAULT_FRAME_DURATION]
        
    num_output_frames = max(len(raw_frames), len(pattern))
    
    output = []
        
    # Cycle frames and durations to max(len(frames), len(pattern))
    for i in range(num_output_frames):
        output.append(
            (raw_frames[i % len(raw_frames)], pattern[i % len(pattern)])
        )
    
    return output


def rotate_animation(
    animation: RotateAnimation,
    raw_frames: list[Image.Image],
) -> list[tuple[Image.Image, int]]:
    
    if animation.degrees_per_frame == 0:
        raise AnimationError("degrees per frame must not be 0")   
    
    frame_count = int(
        round(animation.total_degrees / abs(animation.degrees_per_frame))
    )
    
    if (animation.total_degrees < 360
        or (animation.total_degrees == 360
            and animation.boomerang
        )
    ):
        frame_count += 1
    
    source_frame = raw_frames[0]
    
    max_dimension = math.ceil(math.sqrt(
        (source_frame.width ** 2) + (source_frame.height ** 2)
        ))
    
    new_canvas_size = (max_dimension, max_dimension)
    
    output = []
    
    for i in range(frame_count):
        angle = i * animation.degrees_per_frame
        rotated_frame = source_frame.rotate(-angle, expand=True)
        new_canvas = Image.new("RGBA", new_canvas_size, (0,0,0,0))
        offset = (
            (max_dimension - rotated_frame.width) // 2,
            (max_dimension - rotated_frame.height) // 2,
        )
        new_canvas.paste(rotated_frame, offset, rotated_frame)
        output.append((new_canvas, animation.duration_ms))

    if animation.boomerang and len(output) > 1:
        output = output + output[-2:0:-1]

    return output
   

def build_animation(
    loaded_project: LoadedProject
) -> list[tuple[Image.Image, int]]:
    
    # Error if no frames found
    if len(loaded_project.frames) == 0:
        raise AnimationError(
            f"No frames found in {loaded_project.project.sources.frames}"
            )
    
    # Load images
    raw_frames = []
    frame_dimensions = None
    for frame in loaded_project.frames:
        raw_frame = load_frame(frame)
        
        # Validate all frames have the same size 
        if frame_dimensions is None:
            frame_dimensions = raw_frame.size
        elif raw_frame.size != frame_dimensions:
            raise AnimationError("Frame dimensions do not match")
        raw_frames.append(raw_frame)
    
    # Load and validate background if needed
    background_frame = None
    if loaded_project.background:
        background_frame = load_frame(loaded_project.background)
        
        if background_frame.size != frame_dimensions:
            raise AnimationError(
                "Background frame dimensions do not match rest of frames"
                )
    
    # Animate frames
    animation = loaded_project.project.animation
    match animation.mode:
        case "timing":
            frames =  timing_animation(animation, raw_frames)
        case "rotate":
            frames =  rotate_animation(animation, raw_frames)
        case _:
            raise AnimationError(
                f"Animation type ({animation.mode}) not yetimplemented"
            )
    
    return frames
