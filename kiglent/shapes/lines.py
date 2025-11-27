from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from kiglent.shapes import ShapeBase, _get_segment
from kiglent.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA
from kiglent.vector import Vec2

if TYPE_CHECKING:
    from kiglent.graphics import Batch, Group
    from kiglent.graphics.shader import ShaderProgram
    from kiglent.customtypes import ColorValue, Color4


__all__ = ['Line', 'MultiLine', 'Lines']


class Line(ShapeBase):
    def __init__(
            self,
            x: float, y: float, x2: float, y2: float,
            thickness: float = 1.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a line.

        The line's anchor point defaults to the center of the line's
        thickness on the X axis, and the Y axis.

        Args:
            x:
                The first X coordinate of the line.
            y:
                The first Y coordinate of the line.
            x2:
                The second X coordinate of the line.
            y2:
                The second Y coordinate of the line.
            thickness:
                The desired width of the line.
            color:
                The RGB or RGBA color of the line, specified as a
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
        self._x2 = x2
        self._y2 = y2

        self._thickness = thickness
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(6,blend_src, blend_dest, batch, group, program)

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        vec_ab = Vec2(self._x2 - self._x, self._y2 - self._y)
        vec_ba = Vec2(self._x - self._x2, self._y - self._y2)
        vec_ap = Vec2(point[0] - self._x - self._anchor_x, point[1] - self._y + self._anchor_y)
        vec_bp = Vec2(point[0] - self._x2 - self._anchor_x, point[1] - self._y2 + self._anchor_y)
        if vec_ab.dot(vec_ap) * vec_ba.dot(vec_bp) < 0:
            return False

        a, b = point[0] + self._anchor_x, point[1] - self._anchor_y
        x1, y1, x2, y2 = self._x, self._y, self._x2, self._y2
        # The following is the expansion of the determinant of a 3x3 matrix
        # used to calculate the area of a triangle.
        double_area = abs(a * y1 + b * x2 + x1 * y2 - x2 * y1 - a * y2 - b * x1)
        h = double_area / math.dist((self._x, self._y), (self._x2, self._y2))
        return h < self._thickness / 2

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            6, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x1 = 0
        y1 = -self._thickness / 2
        x2 = x1 + math.hypot(self._y2 - self._y, self._x2 - self._x)
        y2 = y1 + self._thickness

        r = math.atan2(self._y2 - self._y, self._x2 - self._x)
        cr = math.cos(r)
        sr = math.sin(r)
        anchor_x = self._anchor_x
        anchor_y = self._anchor_y
        ax = x1 * cr - y1 * sr - anchor_x
        ay = x1 * sr + y1 * cr - anchor_y
        bx = x2 * cr - y1 * sr - anchor_x
        by = x2 * sr + y1 * cr - anchor_y
        cx = x2 * cr - y2 * sr - anchor_x
        cy = x2 * sr + y2 * cr - anchor_y
        dx = x1 * cr - y2 * sr - anchor_x
        dy = x1 * sr + y2 * cr - anchor_y

        return ax, ay, bx, by, cx, cy, ax, ay, cx, cy, dx, dy

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def thickness(self) -> float:
        """The thickness of the line."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: float) -> None:
        self._thickness = thickness
        self._update_vertices()

    @property
    def x2(self) -> float:
        """Get/set the 2nd X coordinate of the line."""
        return self._x2

    @x2.setter
    def x2(self, value: float) -> None:
        self._x2 = value
        self._update_vertices()

    @property
    def y2(self) -> float:
        """Get/set the 2nd Y coordinate of the line."""
        return self._y2

    @y2.setter
    def y2(self, value: float) -> None:
        self._y2 = value
        self._update_vertices()
    
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               x2: float | None = None, y2: float | None = None, thickness: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
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

        if x2 is not None:
            self._x2 = x2
            verticles = True
        if y2 is not None:
            self._y2 = y2
            verticles = True

        if thickness is not None:
            self._thickness = thickness
            verticles = True

        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
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


class MultiLine(ShapeBase):
    def __init__(
            self,
            *coordinates: tuple[float, float] | Sequence[float],
            closed: bool = False,
            thickness: float = 1.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create multiple connected lines from a series of coordinates.

        The shape's anchor point defaults to the first vertex point.

        Args:
            coordinates:
                The coordinates for each point in the shape. Each must
                unpack like a tuple consisting of an X and Y float-like
                value.
            closed:
                Set this to ``True`` to add a line connecting the first
                and last points. The default is ``False``
            thickness:
                The desired thickness or width used for the line segments.
            color:
                The RGB or RGBA color of the shape, specified as a
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
        # len(self._coordinates) = the number of vertices in the shape.
        self._thickness = thickness
        self._closed = closed
        self._rotation = 0
        self._coordinates = list(coordinates)
        self._x, self._y = self._coordinates[0]

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            (len(self._coordinates) - 1 + closed) * 6,
            blend_src, blend_dest, batch, group, program,
        )

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        trans_x, trans_y = self._coordinates[0]
        trans_x += self._anchor_x
        trans_y += self._anchor_y
        coords: list[list[float]] = [[x - trans_x, y - trans_y] for x, y in self._coordinates]
        if self._closed:
            coords.append(coords[0])

        # Create a list of triangles from segments between 2 points:
        triangles = []
        prev_miter = None
        prev_scale = None
        for i in range(len(coords) - 1):
            prev_point: list[float] | None = None
            next_point: list[float] | None = None
            if i > 0:
                prev_point = coords[i - 1]

            if i + 2 < len(coords):
                next_point = coords[i + 2]

            prev_miter, prev_scale, *segment = _get_segment(prev_point, coords[i], coords[i + 1], next_point,
                                                            self._thickness, prev_miter, prev_scale)
            triangles.extend(segment)

        return triangles

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def thickness(self) -> float:
        """Get/set the line thickness of the multi-line."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: float) -> None:
        self._thickness = thickness
        self._update_vertices()
    
    
    def update(self,
               coordinates: Sequence[tuple[float, float]] | None = None, closed: bool | None = None,
               thickness: float | None = None, z: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        verticles = False
        
        if closed is not None:
            self._closed = closed
            verticles = True
        
        if coordinates is not None:
            x, y =coordinates[0]
            self._x = x
            self._y = y
            self._update_translation()
            
            self._coordinates = list(coordinates)
            verticles = True

        if z is not None:
            self.z = z
        
        if thickness is not None:
            self._thickness = thickness
            verticles = True
        
        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
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

Lines = MultiLine

