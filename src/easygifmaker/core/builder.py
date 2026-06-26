# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image
from math import lcm, ceil, sqrt

from .project import LoadedProject
from .schemas import RotateMotion, MoveMotion

from easygifmaker.exceptions import AnimationError


def animation_pipeline(
    loaded_project: LoadedProject
) -> list[tuple[Image.Image, int]]:
    
    # Error if no frames found
    if len(loaded_project.frames) == 0:
        raise AnimationError(
            f"No frames found in {loaded_project.project.sources.frames}"
    )
    
    # Load images
    source_frames = []
    frame_dimensions = None
    for frame in loaded_project.frames:
        source_frame = load_frame(frame)
        
        # Validate all frames have the same size 
        if frame_dimensions is None:
            frame_dimensions = source_frame.size
        elif source_frame.size != frame_dimensions:
            raise AnimationError("Frame dimensions do not match")
        source_frames.append(source_frame)
    
    # Load and validate background if needed
    background_frame = None
    if loaded_project.background:
        background_frame = load_frame(loaded_project.background)
        
        if background_frame.size != frame_dimensions:
            raise AnimationError(
                "Background frame dimensions do not match rest of frames"
            )
    else:
        # Create a new transparent background
        background_frame = Image.new("RGBA", frame_dimensions, (0,0,0,0))
    
    source_timing = loaded_project.project.source_timing
    motions = loaded_project.project.motions
    
    # Run motion specific error checking
    for motion in motions:
        if motion.motion_type == "rotate":
            if motion.degrees_per_frame == 0:
                raise AnimationError("degrees per frame must not be 0")
    
    output_duration_ms = loaded_project.project.output.duration_ms

    if motions:
        output_frame_count = lcm(*[motion.frame_count for motion in motions])
    else:
        output_frame_count = len(source_timing.pattern)
    
    output_frames = []

    for i in range(output_frame_count):
        if motions:
            elapsed_ms = i * output_duration_ms
            working_frame = sample_source_at_time(
                source_frames,
                source_timing,
                elapsed_ms,
            )
        else:
            working_frame = source_frames[i % len(source_frames)]
            output_duration_ms = source_timing.pattern[i]
            
        for motion in motions:
            local_index = i % motion.frame_count
            if motion.motion_type == "rotate":
                max_dimension = ceil(
                    sqrt(
                        (background_frame.width ** 2)
                        + (background_frame.height ** 2)
                    )
                )
                working_frame = apply_rotate_motion(
                    motion,
                    working_frame,
                    local_index,
                    max_dimension,
                )
            elif motion.motion_type == "move":
                #TODO add apply_move_motion()
                pass
        
        composite_frame = background_frame.copy()
        offset = (
            (composite_frame.width - working_frame.width) // 2,
            (composite_frame.height - working_frame.height) // 2,
        )
        composite_frame.paste(working_frame, offset, working_frame)
        
        output_frames.append((composite_frame, output_duration_ms))
        
    return output_frames

def load_frame(path: Path) -> Image.Image:
    """Load a single PNG and convert to RGBA"""
    
    frame = Image.open(path).copy()
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")
         
    return frame

def sample_source_at_time(
    frames: list[Image.Image],
    timing: list[int],
    elapsed_ms: int,
) -> Image.Image:
    if timing.pattern is None or len(timing.pattern) == 0:
        return frames[0]

    cycle_duration = sum(timing.pattern)
    time_in_cycle = elapsed_ms % cycle_duration

    cumulative = 0
    for index, duration in enumerate(timing.pattern):
        cumulative += duration
        if time_in_cycle < cumulative:
            return frames[index % len(frames)]

def apply_rotate_motion(
    motion: RotateMotion,
    input_frame: Image.Image,
    index: int,
    max_dimension: int,
) -> Image.Image:
    
    output_frame_size = (max_dimension, max_dimension)
    
    angle = index * motion.degrees_per_frame
    rotated_frame = input_frame.rotate(-angle, expand=True)
    output_frame = Image.new("RGBA", output_frame_size, (0,0,0,0))
    offset = (
        (max_dimension - rotated_frame.width) // 2,
        (max_dimension - rotated_frame.height) // 2,
    )
    output_frame.paste(rotated_frame, offset, rotated_frame)

    return output_frame