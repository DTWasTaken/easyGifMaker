# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The project.json file schema"""

from enum import StrEnum

from pathlib import Path
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Literal, Annotated
    

class SourceTiming(BaseModel):
    pattern: list[int] | None = None
    default_duration_ms: int = 200  # duration of each frame if no pattern given
    
    @field_validator("pattern")
    @classmethod
    def durations_must_be_positive(cls, v):
        if any(d <= 0 for d in v):
            raise ValueError("durations must be positive")
        return v
    
class RotateMotion(BaseModel):
    motion_type: Literal["rotate"] = "rotate"
    boomerang: bool = False
    degrees_per_frame: float
    total_degrees: float = 360.0
    
    @computed_field
    @property
    def frame_count(self) -> int:
        return int(round(self.total_degrees / abs(self.degrees_per_frame)))
    
class AnchorPoints(StrEnum):
    CENTER = 'center'
    TOP_LEFT = 'top left'
    TOP_RIGHT = 'top right'
    BOTTOM_LEFT = 'bottom left'
    BOTTOM_RIGHT = 'bottom right'
    
class LineSegment(BaseModel):
    segment_type: Literal["line"] = "line"
    end: tuple[float, float]

class BezierSegment(BaseModel):
    segment_type: Literal["bezier"] = "bezier"
    control1: tuple[float, float]
    control2: tuple[float, float]
    end: tuple[float, float]

Segment = LineSegment | BezierSegment
    
class MoveMotion(BaseModel):
    motion_type: Literal["move"] = "move"
    boomerang: bool = False
    start: tuple[float, float]
    segments: list[Segment]
    anchor: AnchorPoints = AnchorPoints.CENTER
    frame_count: int = 24
    
class ProjectSources(BaseModel):
    frames: Path
    background: Path | None = None
    
class ProjectOutput(BaseModel):
    filename: str = "out.gif"
    loop: int = 0
    duration_ms: int = 200   # duration of each output frame
    
Motion = Annotated[
    RotateMotion | MoveMotion,
    Field(discriminator="motion_type")
]
    
class Project(BaseModel):
    version: int = 2
    sources: ProjectSources
    source_timing: SourceTiming
    motions: list[Motion] = []
    output: ProjectOutput
