# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Parses and validates a project.json file"""

import json
from pathlib import Path
from pydantic import ValidationError
from dataclasses import dataclass
from natsort import natsorted

from .schemas import Project
from easygifmaker.exceptions import ProjectLoadError


@dataclass
class LoadedProject:
    project: Project        # the parsed Pydantic model
    frames: list[Path]      # absolute, sorted PNG paths
    background: Path | None # absolute path if present
    output_path: Path       # absolute output path
    
def scan_frames_dir(frames_dir: Path) -> list[Path]:
    # Load frames, error on non-PNGs but ignore hidden files
    frames = []
    
    for entry in frames_dir.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            raise ProjectLoadError(
                f"unexpected directory in frames folder: {entry}"
            )
        if entry.suffix.lower() != ".png":
            raise ProjectLoadError(f"unexpected file in frames folder: {entry}")
        frames.append(entry)
       
    # natsort frame names so names with 1,2,...,10,11,... sort as expected
    return natsorted(frames)


def parse_project(project_path: Path) -> Project:
    
    """reads json from path, return validated Project"""

    try:
        with open(project_path, 'r') as f:
            data = json.load(f)
       
        return Project.model_validate(data)
    except ValidationError as e:
        raise ProjectLoadError(f"invalid project file: {e}") from e
    except FileNotFoundError as e:
        raise ProjectLoadError(f"project file not found: {project_path}") from e


def load_project(project: Project, project_dir: Path) -> LoadedProject:
    
    """resolves paths, scans frames, returns absolute paths"""
       
    # Resolve frames_path if not absolute from the CLI
    frames_path = project.sources.frames
    if not frames_path.is_absolute():
        frames_path = (project_dir / frames_path).resolve()
        
    # Check frames path exists
    if not frames_path.exists():
        raise ProjectLoadError(f"frame(s) not found: {frames_path}")
  
    # Check if frames_path is a directory or a single png
    if frames_path.is_dir():
        frames = scan_frames_dir(frames_path)
    elif frames_path.is_file():
        if frames_path.suffix.lower() != ".png":
            raise ProjectLoadError(f"given frame is not a png: {frames_path}")
        frames = [frames_path]
    else:
        raise ProjectLoadError(f"frame(s) not found: {frames_path}")
   
    # Resolve output_path if not absolute from the CLI
    output_path = project.output.filename
    if not Path(output_path).is_absolute():
        output_path = (project_dir / output_path).resolve()
   
    # Get background or None
    if project.sources.background:
        background = (project_dir / project.sources.background).resolve()
    else:
        background = None
    
    return LoadedProject(project, frames, background, output_path)