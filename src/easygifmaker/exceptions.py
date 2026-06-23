# SPDX-FileCopyrightText: 2026 Dan Terry <dan@danielterry.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

class EasyGifMakerError(Exception):
    """Base exception for the project."""

class ProjectLoadError(EasyGifMakerError):
    """Raised when a project file or its assets cannot be loaded."""

class AnimationError(EasyGifMakerError):
    """Raised when a valid project cannot be rendered as an animation."""