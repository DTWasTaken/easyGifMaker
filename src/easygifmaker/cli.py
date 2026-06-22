# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""CLI entry point for easyGifMaker"""

import argparse

from pathlib import Path

from easygifmaker.core import load_frame, load_frames, save_gif


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an animated GIF from PNGs")
    parser.add_argument("-o", "--output", default="out.gif", help="Output GIF path")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    timing = subparsers.add_parser(
        "timing",
        help="Creates a GIF that is a series of PNGs"
        )
    timing.add_argument(
        "frames_dir",
        type=Path,
        help="Path to folder with PNG files to combine"
        )
    timing.add_argument(
        "-p",
        "--pattern",
        help="Frame duration pattern in ms"
        )
    
    move = subparsers.add_parser(
        "move",
        help="Applies a movement to a single PNG with an optional background"
        )
   
    args = parser.parse_args()
    
    if args.command == "timing":
        pattern = args.pattern.split(',')
        frames = load_frames(args.frames_dir)
        save_gif(frames, args.output, pattern=pattern)
        print(f"Saved {args.output}")
    elif args.command == "move":
        raise NotImplementedError("the Move command is not yet implemented")


if __name__ == "__main__":
    main()