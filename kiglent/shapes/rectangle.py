from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from kiglent.shapes import ShapeBase, _rotate_point
from kiglent.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA

if TYPE_CHECKING:
    from kiglent.graphics import Batch, Group
    from kiglent.graphics.shader import ShaderProgram
    from kiglent.customtypes import Color4, ColorValue


__all__ = ['Rectangle', 'BorderedRectangle', 'RoundedRectangle', 'Frame',
           'Rect', 'BorderedRect', 'RectBordered', 'RoundedRect', 'RectRounded', 'Box']


class Rectangle(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            width: float, height: float,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = 0.0
        self._width = width
        self._height = height
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(6, blend_src, blend_dest, batch, group, program)

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        x, y = self._x - self._anchor_x, self._y - self._anchor_y
        return x < point[0] < x + self._width and y < point[1] < y + self._height

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            6, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            x1 = -self._anchor_x
            y1 = -self._anchor_y
            x2 = x1 + self._width
            y2 = y1 + self._height

            return x1, y1, x2, y1, x2, y2, x1, y1, x2, y2, x1, y2

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()
    
    @property
    def width_anchored(self) -> float:
        return self._width
    
    @width_anchored.setter
    def width_anchored(self, value: float) -> None:
        self._anchor_x = self._anchor_x / self._width * value
        self._width = value
        self._update_vertices()
    
    @property
    def height_anchored(self) -> float:
        return self._height
    
    @height_anchored.setter
    def height_anchored(self, value: float) -> None:
        self._anchor_y = self._anchor_y / self._height * value
        self._height = value
        self._update_vertices()
    
    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._width
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._width * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._height
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._height * value
        self._update_vertices()
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               width: float | None = None, height: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               width_anchored: float | None = None, height_anchored: float | None = None,
               anchor_scale_x: float | None = None, anchor_scale_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        translation = False
        verticles = False
        
        if x is not None:
            self._x = x
            translation = True
        if y is not None:
            self._y = y
            translation = True

        if translation:
            self._update_translation()

        if z is not None:
            self.z = z

        if width is not None:
            self._width = width
            verticles = True
        if height is not None:
            self._height = height
            verticles = True

        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if width_anchored is not None:
            self._anchor_x = self._anchor_x / self._width * width_anchored
            self._width = width_anchored
            verticles = True
        if height_anchored is not None:
            self._anchor_y = self._anchor_y / self._height * height_anchored
            self._height = height_anchored
            verticles = True
        
        if anchor_scale_x is not None:
            self._anchor_x = self._width * anchor_scale_x
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = self._width * anchor_scale_y
            verticles = True

        if visible is not None:
            self._visible = visible
            verticles = True

        if verticles:
            self._update_vertices()


        if rotation is not None:
            self.rotation = rotation


        if color is not None:
            if opacity is not None:
                self._rgba = (*color[:3], opacity)
            else:
                self._rgba = (*color[:3], self._rgba[3])
            self._update_color()

        elif opacity is not None:
            self._rgba = (*self._rgba[:3], opacity)
            self._update_color()
        

Rect = Rectangle


class BorderedRectangle(ShapeBase):
    def __init__(
            self,
            x: float, y: float, width: float, height: float,
            border: float = 1.0,
            color: ColorValue = (255, 255, 255),
            border_color: ColorValue = (100, 100, 100),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a bordered rectangle.

        The rectangle's anchor point defaults to the ``(x, y)`` coordinates,
        which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            border:
                The thickness of the border.
            color:
                The RGB or RGBA fill color of the rectangle, specified
                as a tuple of 3 or 4 ints in the range of 0-255. RGB
                colors will be treated as having an opacity of 255.
            border_color:
                The RGB or RGBA fill color of the border, specified
                as a tuple of 3 or 4 ints in the range of 0-255. RGB
                colors will be treated as having an opacity of 255.

                The alpha values must match if you pass RGBA values to
                both this argument and `border_color`. If they do not,
                a `ValueError` will be raised informing you of the
                ambiguity.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = 0.0
        self._width = width
        self._height = height
        self._rotation = 0
        self._border = border

        fill_r, fill_g, fill_b, *fill_a = color
        border_r, border_g, border_b, *border_a = border_color

        # Start with a default alpha value of 255.
        alpha = 255
        # Raise Exception if we have conflicting alpha values
        if fill_a and border_a and fill_a[0] != border_a[0]:
            raise ValueError("When color and border_color are both RGBA values,"
                             "they must both have the same opacity")

        # Choose a value to use if there is no conflict
        elif fill_a:
            alpha = fill_a[0]
        elif border_a:
            alpha = border_a[0]

        # Although the shape is only allowed one opacity, the alpha is
        # stored twice to keep other code concise and reduce cpu usage
        # from stitching together sequences.
        self._rgba = fill_r, fill_g, fill_b, alpha
        self._border_rgba = border_r, border_g, border_b, alpha

        super().__init__(8, blend_src, blend_dest, batch, group, program)

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        x, y = self._x - self._anchor_x, self._y - self._anchor_y
        return x < point[0] < x + self._width and y < point[1] < y + self._height

    def _create_vertex_list(self) -> None:
        indices = [0, 1, 2, 0, 2, 3, 0, 4, 3, 4, 7, 3, 0, 1, 5, 0, 5, 4, 1, 2, 5, 5, 2, 6, 6, 2, 3, 6, 3, 7]
        self._vertex_list = self._program.vertex_list_indexed(
            8, self._draw_mode, indices, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * 4 + self._border_rgba * 4),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _update_color(self) -> None:
        self._vertex_list.colors[:] = self._rgba * 4 + self._border_rgba * 4

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        bx1 = -self._anchor_x
        by1 = -self._anchor_y
        bx2 = bx1 + self._width
        by2 = by1 + self._height
        b = self._border
        ix1 = bx1 + b
        iy1 = by1 + b
        ix2 = bx2 - b
        iy2 = by2 - b

        return (ix1, iy1, ix2, iy1, ix2, iy2, ix1, iy2,
                bx1, by1, bx2, by1, bx2, by2, bx1, by2)

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def border(self) -> float:
        """The border thickness of the bordered rectangle.

        This extends inward from the edge of the rectangle toward the
        center.
        """
        return self._border

    @border.setter
    def border(self, thickness: float) -> None:
        self._border = thickness
        self._update_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the bordered rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the bordered rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    @property
    def width_anchored(self) -> float:
        return self._width
    
    @width_anchored.setter
    def width_anchored(self, value: float) -> None:
        self._anchor_x = self._anchor_x / self._width * value
        self._width = value
        self._update_vertices()
    
    @property
    def height_anchored(self) -> float:
        return self._height
    
    @height_anchored.setter
    def height_anchored(self, value: float) -> None:
        self._anchor_y = self._anchor_y / self._height * value
        self._height = value
        self._update_vertices()
    
    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._width
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._width * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._height
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._height * value
        self._update_vertices()
    
    @property
    def border_color(self) -> Color4:
        """Get/set the bordered rectangle's border color.

        To set the color of the interior fill, see :py:attr:`.color`.

        You can set the border color to either of the following:

        * An RGBA tuple of integers ``(red, green, blue, alpha)``
        * An RGB tuple of integers ``(red, green, blue)``

        Setting the alpha on this property will change the alpha of
        the entire shape, including both the fill and the border.

        Each color component must be in the range 0 (dark) to 255 (saturated).
        """
        return self._border_rgba

    @border_color.setter
    def border_color(self, values: ColorValue) -> None:
        r, g, b, *a = values

        if a:
            alpha = a[0]
        else:
            alpha = self._rgba[3]

        self._border_rgba = r, g, b, alpha
        self._rgba = *self._rgba[:3], alpha

        self._update_color()

    @property
    def color(self) -> ColorValue:
        """Get/set the bordered rectangle's interior fill color.

        To set the color of the border outline, see
        :py:attr:`.border_color`.

        The color may be specified as either of the following:

        * An RGBA tuple of integers ``(red, green, blue, alpha)``
        * An RGB tuple of integers ``(red, green, blue)``

        Setting the alpha through this property will change the alpha
        of the entire shape, including both the fill and the border.

        Each color component must be in the range 0 (dark) to 255
        (saturated).
        """
        return self._rgba

    @color.setter
    def color(self, values: ColorValue) -> None:
        r, g, b, *a = values

        if a:
            alpha = a[0]
        else:
            alpha = self._rgba[3]

        self._rgba = r, g, b, alpha
        self._border_rgba = *self._border_rgba[:3], alpha
        self._update_color()
    
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               width: float | None = None, height: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               width_anchored: float | None = None, height_anchored: float | None = None,
               anchor_scale_x: float | None = None, anchor_scale_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               border: float | None = None, border_color: ColorValue | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        translation = False
        verticles = False
        colored = False
        
        if x is not None:
            self._x = x
            translation = True
        if y is not None:
            self._y = y
            translation = True

        if translation:
            self._update_translation()

        if z is not None:
            self.z = z

        if width is not None:
            self._width = width
            verticles = True
        if height is not None:
            self._height = height
            verticles = True

        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if width_anchored is not None:
            self._anchor_x = self._anchor_x / self._width * width_anchored
            self._width = width_anchored
            verticles = True
        if height_anchored is not None:
            self._anchor_y = self._anchor_y / self._height * height_anchored
            self._height = height_anchored
            verticles = True
        
        if anchor_scale_x is not None:
            self._anchor_x = self._width * anchor_scale_x
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = self._width * anchor_scale_y
            verticles = True

        if border is not None:
            self._border = border
            verticles = True

        if visible is not None:
            self._visible = visible
            verticles = True

        if verticles:
            self._update_vertices()


        if rotation is not None:
            self.rotation = rotation

        if border_color is not None:
            if opacity is not None:
                self._border_rgba = (*border_color[:3], opacity)
            else:
                self._border_rgba = (*border_color[:3], self._border_rgba[3])
            colored = True
        
        if color is not None:
            if opacity is not None:
                self._rgba = (*color[:3], opacity)
            else:
                self._rgba = (*color[:3], self._rgba[3])
            colored = True

        if opacity is not None:
            self._rgba = (*self._rgba[:3], opacity)
            self._border_rgba = (*self._border_rgba[:3], opacity)
            colored = True
        
        if colored:
            self._update_color()
        

BorderedRect = RectBordered = BorderedRectangle


_RadiusT = float | tuple[float, float]

class RoundedRectangle(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            width: float, height: float,
            radius: _RadiusT | tuple[_RadiusT, _RadiusT, _RadiusT, _RadiusT],
            segments: int | tuple[int, int, int, int] | None = None,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a rectangle with rounded corners.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            radius:
                One or four values to specify the radii used for the rounded corners.
                If one value is given, all corners will use the same value. If four values
                are given, it will specify the radii used for the rounded corners clockwise:
                bottom-left, top-left, top-right, bottom-right. A value can be either a single
                float, or a tuple of two floats to specify different x,y dimensions.
            segments:
                You can optionally specify how many distinct triangles each rounded corner
                should be made from. This can be one int for all corners, or a tuple of
                four ints for each corner, specified clockwise: bottom-left, top-left,
                top-right, bottom-right. If no value is specified, it will automatically
                calculated using the formula: ``max(14, int(radius / 1.25))``.
            color:
                The RGB or RGBA color of the rectangle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = 0.0
        self._width = width
        self._height = height
        self._set_radius(radius)
        self._set_segments(segments)
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            (sum(self._segments) + 4) * 3,
            blend_src, blend_dest, batch, group, program,
        )

    def _set_radius(self, radius: _RadiusT | tuple[_RadiusT, _RadiusT, _RadiusT, _RadiusT]) -> None:
        if isinstance(radius, (int, float)):
            self._radius = ((radius, radius),) * 4
        elif len(radius) == 2:
            self._radius = (radius,) * 4
        else:
            assert len(radius) == 4
            self._radius = []
            for value in radius:
                if isinstance(value, (int, float)):
                    self._radius.append((value, value))
                else:
                    assert len(value) == 2
                    self._radius.append(value)

    def _set_segments(self, segments: int | tuple[int, int, int, int] | None) -> None:
        if segments is None:
            self._segments = tuple(int(max(a, b) / 1.25) for a, b in self._radius)
        elif isinstance(segments, int):
            self._segments = (segments,) * 4
        else:
            assert len(segments) == 4
            self._segments = segments

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        x, y = self._x - self._anchor_x, self._y - self._anchor_y
        return x < point[0] < x + self._width and y < point[1] < y + self._height

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y

        points = []
        # arc_x, arc_y, start_angle
        arc_positions = [
            # bottom-left
            (x + self._radius[0][0],
             y + self._radius[0][1], math.pi * 3 / 2),
            # top-left
            (x + self._radius[1][0],
             y + self._height - self._radius[1][1], math.pi),
            # top-right
            (x + self._width - self._radius[2][0],
             y + self._height - self._radius[2][1], math.pi / 2),
            # bottom-right
            (x + self._width - self._radius[3][0],
             y + self._radius[3][1], 0),
        ]

        for (rx, ry), (arc_x, arc_y, arc_start), segments in zip(self._radius, arc_positions, self._segments):
            tau_segs = -math.pi / 2 / segments
            points.extend([(arc_x + rx * math.cos(i * tau_segs + arc_start),
                            arc_y + ry * math.sin(i * tau_segs + arc_start)) for i in range(segments + 1)])

        center_x = self._width / 2 + x
        center_y = self._height / 2 + y
        vertices = []
        for i, point in enumerate(points):
            triangle = center_x, center_y, *points[i - 1], *point
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    @property
    def width_anchored(self) -> float:
        return self._width
    
    @width_anchored.setter
    def width_anchored(self, value: float) -> None:
        self._anchor_x = self._anchor_x / self._width * value
        self._width = value
        self._update_vertices()
    
    @property
    def height_anchored(self) -> float:
        return self._height
    
    @height_anchored.setter
    def height_anchored(self, value: float) -> None:
        self._anchor_y = self._anchor_y / self._height * value
        self._height = value
        self._update_vertices()
    
    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._width
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._width * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._height
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._height * value
        self._update_vertices()
    
    @property
    def radius(self) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
        return self._radius

    @radius.setter
    def radius(self, value: _RadiusT | tuple[_RadiusT, _RadiusT, _RadiusT, _RadiusT]) -> None:
        self._set_radius(value)
        self._update_vertices()
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               radius: _RadiusT | tuple[_RadiusT, _RadiusT, _RadiusT, _RadiusT] | None = None,
               width: float | None = None, height: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               width_anchored: float | None = None, height_anchored: float | None = None,
               anchor_scale_x: float | None = None, anchor_scale_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        translation = False
        verticles = False
        
        if x is not None:
            self._x = x
            translation = True
        if y is not None:
            self._y = y
            translation = True

        if translation:
            self._update_translation()

        if z is not None:
            self.z = z
        
        if radius is not None:
            self._set_radius(radius)
            verticles = True

        if width is not None:
            self._width = width
            verticles = True
        if height is not None:
            self._height = height
            verticles = True

        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if width_anchored is not None:
            self._anchor_x = self._anchor_x / self._width * width_anchored
            self._width = width_anchored
            verticles = True
        if height_anchored is not None:
            self._anchor_y = self._anchor_y / self._height * height_anchored
            self._height = height_anchored
            verticles = True

        if anchor_scale_x is not None:
            self._anchor_x = self._width * anchor_scale_x
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = self._width * anchor_scale_y
            verticles = True

        if visible is not None:
            self._visible = visible
            verticles = True

        if verticles:
            self._update_vertices()


        if rotation is not None:
            self.rotation = rotation


        if color is not None:
            if opacity is not None:
                self._rgba = (*color[:3], opacity)
            else:
                self._rgba = (*color[:3], self._rgba[3])
            self._update_color()

        elif opacity is not None:
            self._rgba = (*self._rgba[:3], opacity)
            self._update_color()

RoundedRect = RectRounded = RoundedRectangle


class Frame(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            width: float, height: float,
            thickness: float = 1.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create an unfilled rectangular shape, with optional thickness.

        The box's anchor point defaults to the ``(x, y)`` coordinates,
        which are placed at the bottom left.
        Changing the thickness of the box will extend the walls inward;
        the outward dimensions will not be affected.

        Args:
            x:
                The X coordinate of the box.
            y:
                The Y coordinate of the box.
            width:
                The width of the box.
            height:
                The height of the box.
            thickness:
                The thickness of the lines that make up the box.
            color:
                The RGB or RGBA color of the box, specified as a tuple
                of 3 or 4 ints in the range of 0-255. RGB colors will
                be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = 0.0
        self._width = width
        self._height = height
        self._thickness = thickness

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(8, blend_src, blend_dest, batch, group, program)

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        x, y = self._x - self._anchor_x, self._y - self._anchor_y
        return x < point[0] < x + self._width and y < point[1] < y + self._height

    def _create_vertex_list(self) -> None:
        #   3--------6
        #   | 2    7 |
        #   | 1    4 |
        #   0--------5
        indices = [0, 1, 2, 0, 2, 3, 0, 5, 4, 0, 4, 1, 4, 5, 6, 4, 6, 7, 2, 7, 6, 2, 6, 3]
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts, self._draw_mode, indices, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _update_color(self):
        self._vertex_list.colors[:] = self._rgba * self._num_verts

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        t = self._thickness
        left = -self._anchor_x
        bottom = -self._anchor_y
        right = left + self._width
        top = bottom + self._height

        x1 = left
        x2 = left + t
        x3 = right - t
        x4 = right
        y1 = bottom
        y2 = bottom + t
        y3 = top - t
        y4 = top
        #     |  0   |   1   |   2   |   3   |   4   |   5   |   6   |   7   |
        return x1, y1, x2, y2, x2, y3, x1, y4, x3, y2, x4, y1, x4, y4, x3, y3

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set the width of the box.

        Setting the width will position the left and right sides
        relative to the box's :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the Box.

        Setting the height will set the bottom and top relative to the
        box's :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    @property
    def width_anchored(self) -> float:
        return self._width
    
    @width_anchored.setter
    def width_anchored(self, value: float) -> None:
        self._anchor_x = self._anchor_x / self._width * value
        self._width = value
        self._update_vertices()
    
    @property
    def height_anchored(self) -> float:
        return self._height
    
    @height_anchored.setter
    def height_anchored(self, value: float) -> None:
        self._anchor_y = self._anchor_y / self._height * value
        self._height = value
        self._update_vertices()
    
    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._width
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._width * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._height
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._height * value
        self._update_vertices()
    
    @property
    def thickness(self) -> float:
        """Get/set the line thickness of the Box."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: float) -> None:
        self._thickness = thickness
        self._update_vertices()
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               thickness: float | None = None,
               width: float | None = None, height: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               width_anchored: float | None = None, height_anchored: float | None = None,
               anchor_scale_x: float | None = None, anchor_scale_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        translation = False
        verticles = False
        
        if x is not None:
            self._x = x
            translation = True
        if y is not None:
            self._y = y
            translation = True

        if translation:
            self._update_translation()

        if z is not None:
            self.z = z
        
        if thickness is not None:
            self._thickness = thickness
            verticles = True

        if width is not None:
            self._width = width
            verticles = True
        if height is not None:
            self._height = height
            verticles = True

        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if width_anchored is not None:
            self._anchor_x = self._anchor_x / self._width * width_anchored
            self._width = width_anchored
            verticles = True
        if height_anchored is not None:
            self._anchor_y = self._anchor_y / self._height * height_anchored
            self._height = height_anchored
            verticles = True

        if anchor_scale_x is not None:
            self._anchor_x = self._width * anchor_scale_x
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = self._width * anchor_scale_y
            verticles = True

        if visible is not None:
            self._visible = visible
            verticles = True

        if verticles:
            self._update_vertices()


        if rotation is not None:
            self.rotation = rotation


        if color is not None:
            if opacity is not None:
                self._rgba = (*color[:3], opacity)
            else:
                self._rgba = (*color[:3], self._rgba[3])
            self._update_color()

        elif opacity is not None:
            self._rgba = (*self._rgba[:3], opacity)
            self._update_color()

Box = Frame

