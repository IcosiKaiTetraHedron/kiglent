"""Holds type aliases used throughout the codebase."""

from typing import Literal


AnchorX = Literal["left", "center", "right"]
AnchorY = Literal["top", "bottom", "center", "baseline"]
HorizontalAlign = Literal["left", "center", "right"]
ContentVAlign = Literal["bottom", "center", "top"]

Color4 = tuple[int, int, int, int]
Color3 = tuple[int, int, int]
ColorValue = Color4 | Color3


__all__ = ["AnchorX", "AnchorY", "HorizontalAlign", "ContentVAlign", "Color4", "Color3", "ColorValue"]
