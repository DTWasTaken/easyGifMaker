# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The project.json file schema"""

from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class TimingAnimation(BaseModel):
    mode: Literal["timing"] = "timing"
    pattern: list[int] | None = None
    
    @field_validator("pattern")
    @classmethod
    def durations_must_be_positive(cls, v):
        if any(d <= 0 for d in v):
            raise ValueError("durations must be positive")
        return v
    
class RotateAnimation(BaseModel):
    mode: Literal["rotate"] = "rotate"
    frames: int
    rate: float
    
class ProjectSources(BaseModel):
    frames: Path
    background: Path | None = None
    
class ProjectOutput(BaseModel):
    filename: str = "out.gif"
    loop: int = 0
    
class Project(BaseModel):
    version: int = 1
    sources: ProjectSources
    animation: TimingAnimation | RotateAnimation
    output: ProjectOutput
