from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from kiglent.shapes import ShapeBase, _rotate_point
from kiglent.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA

if TYPE_CHECKING:
    from kiglent.graphics import Batch, Group
    from kiglent.graphics.shader import ShaderProgram
    from kiglent.customtypes import ColorValue, Color4


__all__ = ['Circle', 'Ellipse', 'Sector']


class Circle(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            radius: float,
            segments: int | None = None,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a circle.

        The circle's anchor point (x, y) defaults to the center of the circle.

        Args:
            x:
                X coordinate of the circle.
            y:
                Y coordinate of the circle.
            radius:
                The desired radius.
            segments:
                You can optionally specify how many distinct triangles
                the circle should be made from. If not specified it will
                be automatically calculated using the formula:
                `max(14, int(radius / 1.25))`.
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
        self._radius = radius
        self._segments = segments or max(14, int(radius / 1.25))
        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            self._segments * 3,
            blend_src, blend_dest, batch, group, program,
        )

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        return math.dist((self._x - self._anchor_x, self._y - self._anchor_y), point) < self._radius

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._segments * 3, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y
        r = self._radius
        tau_segs = math.pi * 2 / self._segments

        # Calculate the outer points of the circle:
        points = [(x + (r * math.cos(i * tau_segs)),
                   y + (r * math.sin(i * tau_segs))) for i in range(self._segments)]

        # Create a list of triangles from the points:
        vertices = []
        for i, point in enumerate(points):
            triangle = x, y, *points[i - 1], *point
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def radius(self) -> float:
        """Gets/set radius of the circle."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value
        self._update_vertices()

    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._radius
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._radius * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._radius
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._radius * value
        self._update_vertices()
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               radius: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
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
            self._radius = radius
            verticles = True
        
        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if anchor_scale_x is not None:
            self._anchor_x = anchor_scale_x * self._radius
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = anchor_scale_y * self._radius
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


class Ellipse(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            a: float, b: float,
            segments: int | None = None,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create an ellipse.

        The ellipse's anchor point ``(x, y)`` defaults to the center of
        the ellipse.

        Args:
            x:
                X coordinate of the ellipse.
            y:
                Y coordinate of the ellipse.
            a:
                Semi-major axes of the ellipse.
            b:
                Semi-minor axes of the ellipse.
            segments:
                You can optionally specify how many distinct line segments
                the ellipse should be made from. If not specified it will be
                automatically calculated using the formula:
                ``int(max(a, b) / 1.25)``.
            color:
                The RGB or RGBA color of the ellipse, specified as a
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
        self._a = a
        self._b = b

        # Break with conventions in other _Shape constructors
        # because a & b are used as meaningful variable names.
        color_r, color_g, color_b, *color_a = color
        self._rgba = color_r, color_g, color_b, color_a[0] if color_a else 255

        self._rotation = 0
        self._segments = segments or int(max(a, b) / 1.25)

        super().__init__(
            self._segments * 3,
            blend_src, blend_dest, batch, group, program,
        )

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        # Since directly testing whether a point is inside an ellipse is more
        # complicated, it is more convenient to transform it into a circle.
        point = (self._b / self._a * point[0], point[1])
        shape_center = (self._b / self._a * (self._x - self._anchor_x), self._y - self._anchor_y)
        return math.dist(shape_center, point) < self._b

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._segments * 3, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y
        tau_segs = math.pi * 2 / self._segments

        # Calculate the points of the ellipse by formula:
        points = [(x + self._a * math.cos(i * tau_segs),
                   y + self._b * math.sin(i * tau_segs)) for i in range(self._segments)]

        # Create a list of triangles from the points:
        vertices = []
        for i, point in enumerate(points):
            triangle = x, y, *points[i - 1], *point
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def a(self) -> float:
        """Get/set the semi-major axes of the ellipse."""
        return self._a

    @a.setter
    def a(self, value: float) -> None:
        self._a = value
        self._update_vertices()

    @property
    def b(self) -> float:
        """Get/set the semi-minor axes of the ellipse."""
        return self._b

    @b.setter
    def b(self, value: float) -> None:
        self._b = value
        self._update_vertices()

    @property
    def anchor_scale_x(self) -> float:
        return self._anchor_x / self._a
    @anchor_scale_x.setter
    def anchor_scale_x(self, value: float) -> None:
        self._anchor_x = self._a * value
        self._update_vertices()
    
    @property
    def anchor_scale_y(self) -> float:
        return self._anchor_y / self._b
    @anchor_scale_y.setter
    def anchor_scale_y(self, value: float) -> None:
        self._anchor_y = self._b * value
        self._update_vertices()
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               a: float | None = None, b: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
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

        if a is not None:
            self._a = a
            verticles = True
        if b is not None:
            self._b = b
            verticles = True
        
        if anchor_x is not None:
            self._anchor_x = anchor_x
            verticles = True
        if anchor_y is not None:
            self._anchor_y = anchor_y
            verticles = True

        if anchor_scale_x is not None:
            self._anchor_x = anchor_scale_x * self._a
            verticles = True
        if anchor_scale_y is not None:
            self._anchor_y = anchor_scale_y * self._b
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


class Sector(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            radius: float,
            segments: int | None = None,
            angle: float = 360.0,
            start_angle: float = 0.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a Sector of a circle.

        By default, ``(x, y)`` is used as:
        * The sector's anchor point
        * The center of the circle the sector is cut from

        Args:
            x:
                X coordinate of the sector.
            y:
                Y coordinate of the sector.
            radius:
                The desired radius.
            segments:
                You can optionally specify how many distinct triangles
                the sector should be made from. If not specified it will
                be automatically calculated using the formula:
                `max(14, int(radius / 1.25))`.
            angle:
                The angle of the sector, in degrees. Defaults to 360,
                which is a full circle.
            start_angle:
                The start angle of the sector, in degrees. Defaults to 0.
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
        self._radius = radius
        self._segments = segments or max(14, int(radius / 1.25))

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        self._angle = angle
        self._start_angle = start_angle
        self._rotation = 0

        super().__init__(
            self._segments * 3,
            blend_src, blend_dest, batch, group, program,
        )

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        angle = math.atan2(point[1] - self._y + self._anchor_y, point[0] - self._x + self._anchor_x)
        if angle < 0:
            angle += 2 * math.pi
        if self._start_angle < angle < self._start_angle + self._angle:
            return math.dist((self._x - self._anchor_x, self._y - self._anchor_y), point) < self._radius
        return False

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

        # Calculate the outer points of the sector.
        points = [(x + (r * math.cos((i * segment_radians) + start_radians)),
                   y + (r * math.sin((i * segment_radians) + start_radians))) for i in range(self._segments + 1)]

        # Create a list of triangles from the points
        vertices = []
        for i, point in enumerate(points[1:], start=1):
            triangle = x, y, *points[i - 1], *point
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def angle(self) -> float:
        """The angle of the sector, in degrees."""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = value
        self._update_vertices()

    @property
    def start_angle(self) -> float:
        """The start angle of the sector, in degrees."""
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle: float) -> None:
        self._start_angle = angle
        self._update_vertices()

    @property
    def radius(self) -> float:
        """Get/set the radius of the sector.

        By default, this is in screen pixels. Your drawing / GL settings
        may alter how this is drawn.
        """
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value
        self._update_vertices()

    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               radius: float | None = None, start_angle: float | None = None, angle: float | None = None,
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
