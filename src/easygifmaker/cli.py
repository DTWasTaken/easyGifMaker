# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""CLI entry point for easyGifMaker"""

import argparse
from pathlib import Path

from easygifmaker.core import load_images, save_gif


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an animated GIF from PNGs")
    parser.add_argument("images", nargs="+", help="PNG files to combine")
    parser.add_argument("-o", "--output", default="out.gif", help="Output GIF path")
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=100,
        help="Frame durationin ms"
        )
    args = parser.parse_args()

    frames = load_images(args.images)
    save_gif(frames, args.output, duration_ms=args.duration)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()