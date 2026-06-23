# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""CLI entry point for easyGifMaker"""

import argparse
import sys

from pathlib import Path

from .exceptions import ProjectLoadError, AnimationError

from easygifmaker.core import (
    save_gif,
    parse_project, 
    load_project,
    build_animation
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an animated GIF from PNGs")
    parser.add_argument("--output", help="Output GIF name")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    timing_parse = subparsers.add_parser(
        "timing",
        help="Creates a GIF that is a series of PNGs"
        )
    timing_parse.add_argument(
        "frames_dir",
        type=Path,
        help="Path to folder with PNG files to combine"
        )
    timing_parse.add_argument(
        "-p",
        "--pattern",
        help="Frame duration pattern in ms"
        )
    
    render_parser = subparsers.add_parser("render", help="Render a project file")
    render_parser.add_argument("project", type=Path)
    render_parser.add_argument("--frames", type=Path)
   
    args = parser.parse_args()
   
    if args.command == "render":
        try:
            # Get absolute path for project file
            project_path = args.project.resolve()
            
            # Get validated project object
            project = parse_project(project_path)
            
            # Handle CLI overrides for frames folder and output file name
            if args.frames:
                project.sources.frames = args.frames.resolve()
            if args.output:
                project.output.filename = args.output
            
            # Load the project with sorted and absolute paths
            loaded = load_project(project, project_path.parent)
            
            # Build the animation
            animation = build_animation(loaded)
            
            # Create the gif
            loop = loaded.project.output.loop
            save_gif(animation, loaded.output_path, loop)
            print(f"Rendered {loaded.output_path}")
            
        except ProjectLoadError as e:
            print(f"Failed to load project: {e}", file=sys.stderr)
            sys.exit(1)
        except AnimationError as e:
            print(f"Failed to build animation: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "timing":
        raise NotImplementedError
        #pattern = args.pattern.split(',')
        #frames = load_frames(args.frames_dir)
        #save_gif(frames, args.output, pattern=pattern)
        #print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
