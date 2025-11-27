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


__all__ = ['Arc', 'BezierCurve']


class Arc(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            radius: float,
            segments: int | None = None,
            angle: float = 360.0,
            start_angle: float = 0.0,
            closed: bool = False,
            thickness: float = 1.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create an Arc.

        The Arc's anchor point (x, y) defaults to its center.

        Args:
            x:
                X coordinate of the circle.
            y:
                Y coordinate of the circle.
            radius:
                The desired radius.
            segments:
                You can optionally specify how many distinct line segments
                the arc should be made from. If not specified it will be
                automatically calculated using the formula:
                ``max(14, int(radius / 1.25))``.
            angle:
                The angle of the arc, in degrees. Defaults to 360.0, which is
                a full circle.
            start_angle:
                The start angle of the arc, in degrees. Defaults to 0.
            closed:
                If ``True``, the ends of the arc will be connected with a line.
                defaults to ``False``.
            thickness:
                The desired thickness or width of the line used for the arc.
            color:
                The RGB or RGBA color of the arc, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having opacity of 255.
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
        self._radius = radius
        self._segments = segments or max(14, int(radius / 1.25))

        # handle both 3 and 4 byte colors
        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        self._thickness = thickness
        self._angle = angle
        self._start_angle = start_angle
        # Only set closed if the angle isn't tau
        self._closed = closed if abs(math.tau - self._angle) > 1e-9 else False
        self._rotation = 0

        super().__init__(
            # Each segment is now 6 vertices long
            self._segments * 6 + (6 if self._closed else 0),
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

        x = -self._anchor_x
        y = -self._anchor_y
        r = self._radius
        segment_radians = math.radians(self._angle) / self._segments
        start_radians = math.radians(self._start_angle - self._rotation)

        # Calculate the outer points of the arc:
        points = [(x + (r * math.cos((i * segment_radians) + start_radians)),
                   y + (r * math.sin((i * segment_radians) + start_radians))) for i in range(self._segments + 1)]

        # Create a list of quads from the points
        vertices = []
        prev_miter = None
        prev_scale = None
        for i in range(len(points) - 1):
            prev_point = None
            next_point = None
            if i > 0:
                prev_point = points[i - 1]
            elif self._closed:
                prev_point = points[-1]
            elif abs(self._angle - math.tau) <= 1e-9:
                prev_point = points[-2]

            if i + 2 < len(points):
                next_point = points[i + 2]
            elif self._closed:
                next_point = points[0]
            elif abs(self._angle - math.tau) <= 1e-9:
                next_point = points[1]

            prev_miter, prev_scale, *segment = _get_segment(prev_point, points[i], points[i + 1], next_point,
                                                            self._thickness, prev_miter, prev_scale)
            vertices.extend(segment)

        if self._closed:
            prev_point = None
            next_point = None
            if len(points) > 2:
                prev_point = points[-2]
                next_point = points[1]
            prev_miter, prev_scale, *segment = _get_segment(prev_point, points[-1], points[0], next_point,
                                                            self._thickness, prev_miter, prev_scale)
            vertices.extend(segment)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def radius(self) -> float:
        """Get/set the radius of the arc."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value
        self._update_vertices()

    @property
    def thickness(self) -> float:
        """Get/set the thickness of the Arc."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: float) -> None:
        self._thickness = thickness
        self._update_vertices()

    @property
    def angle(self) -> float:
        """The angle of the arc, in degrees."""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = value
        self._update_vertices()

    @property
    def start_angle(self) -> float:
        """The start angle of the arc, in degrees."""
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle: float) -> None:
        self._start_angle = angle
        self._update_vertices()
    
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               radius: float | None = None, start_angle: float | None = None, angle: float | None = None,
               closed: bool | None = None, thickness: float | None = None,
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

        if radius is not None:
            self._radius = radius
            verticles = True
        
        if start_angle is not None:
            self._start_angle = start_angle
            verticles = True
        if angle is not None:
            self._angle = angle
            verticles = True
        
        if closed is not None:
            self._closed = closed
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


class BezierCurve(ShapeBase):
    def __init__(
            self,
            *points: tuple[float, float],
            t: float = 1.0,
            segments: int = 128,
            thickness: int = 1.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a Bézier curve.

        The curve's anchor point (x, y) defaults to its first control point.

        Args:
            points:
                Control points of the curve. Points can be specified as multiple
                lists or tuples of point pairs. Ex. (0,0), (2,3), (1,9)
            t:
                Draw `100*t` percent of the curve. 0.5 means the curve
                is half drawn and 1.0 means draw the whole curve.
            segments:
                You can optionally specify how many line segments the
                curve should be made from.
            thickness:
                The desired thickness or width of the line used for the curve.
            color:
                The RGB or RGBA color of the curve, specified as a
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
        self._points = list(points)
        self._x, self._y = self._points[0]
        self._t = t
        self._segments = segments
        self._thickness = thickness
        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            self._segments * 6,
            blend_src, blend_dest, batch, group, program,
        )

    def _make_curve(self, t: float) -> list[float]:
        n = len(self._points) - 1
        p = [0, 0]
        for i in range(n + 1):
            m = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
            p[0] += m * self._points[i][0]
            p[1] += m * self._points[i][1]
        return p

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x = -self._anchor_x - self._x
        y = -self._anchor_y - self._y

        # Calculate the points of the curve:
        points = [(x + self._make_curve(self._t * t / self._segments)[0],
                   y + self._make_curve(self._t * t / self._segments)[1]) for t in range(self._segments + 1)]
        trans_x, trans_y = points[0]
        trans_x += self._anchor_x
        trans_y += self._anchor_y
        coords = [[x - trans_x, y - trans_y] for x, y in points]

        # Create a list of doubled-up points from the points:
        vertices = []
        prev_miter = None
        prev_scale = None
        for i in range(len(coords) - 1):
            prev_point = None
            next_point = None
            if i > 0:
                prev_point = points[i - 1]

            if i + 2 < len(points):
                next_point = points[i + 2]

            prev_miter, prev_scale, *segment = _get_segment(prev_point, points[i], points[i + 1], next_point,
                                                            self._thickness, prev_miter, prev_scale)
            vertices.extend(segment)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def points(self) -> list[tuple[float, float]]:
        """Get/set the control points of the Bézier curve."""
        return self._points

    @points.setter
    def points(self, value: list[tuple[float, float]]) -> None:
        self._points = value
        self._update_vertices()

    @property
    def t(self) -> float:
        """Get/set the t in ``100*t`` percent of the curve to draw."""
        return self._t

    @t.setter
    def t(self, value: float) -> None:
        self._t = value
        self._update_vertices()

    @property
    def thickness(self) -> float:
        """Get/set the line thickness for the Bézier curve."""
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: float) -> None:
        self._thickness = thickness
        self._update_vertices()


    def update(self,
               points: Sequence[tuple[float, float]] | None = None, t: float | None = None,
               thickness: float | None = None, z: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        verticles = False
        
        if t is not None:
            self._t = t
            verticles = True
        
        if points is not None:
            x, y =points[0]
            self._x = x
            self._y = y
            self._update_translation()
            
            self._points = list(points)
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

