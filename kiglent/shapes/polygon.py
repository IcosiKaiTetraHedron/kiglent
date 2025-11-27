from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from kiglent.shapes import ShapeBase, _rotate_point
from kiglent.shapes import extra_earcut as earcut
from kiglent.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA

if TYPE_CHECKING:
    from kiglent.graphics import Batch, Group
    from kiglent.graphics.shader import ShaderProgram
    from kiglent.customtypes import ColorValue, Color4


__all__ = ['Triangle', 'Star', 'Polygon']


def _point_in_polygon(polygon: Sequence[tuple[float, float]], point: tuple[float, float]) -> bool:
    """Use raycasting to determine if a point is inside a polygon.

    This function is an example implementation available under MIT License at:
    https://www.algorithms-and-technologies.com/point_in_polygon/python
    """
    odd = False
    i = 0
    j = len(polygon) - 1
    while i < len(polygon) - 1:
        i = i + 1
        if ((polygon[i][1] > point[1]) != (polygon[j][1] > point[1])) and (
                point[0] < ((polygon[j][0] - polygon[i][0]) * (point[1] - polygon[i][1])
                          / (polygon[j][1] - polygon[i][1])) + polygon[i][0]):
            odd = not odd
        j = i
    return odd


class Triangle(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            x2: float, y2: float,
            x3: float, y3: float,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a triangle.

        The triangle's anchor point defaults to the first vertex point.

        Args:
            x:
                The first X coordinate of the triangle.
            y:
                The first Y coordinate of the triangle.
            x2:
                The second X coordinate of the triangle.
            y2:
                The second Y coordinate of the triangle.
            x3:
                The third X coordinate of the triangle.
            y3:
                The third Y coordinate of the triangle.
            color:
                The RGB or RGBA color of the triangle, specified as a
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
        self._x3 = x3
        self._y3 = y3
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(3, blend_src, blend_dest, batch, group, program)

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        return _point_in_polygon(
            [(self._x, self._y), (self._x2, self._y2), (self._x3, self._y3), (self._x, self._y)], point)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            3, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            x1 = -self._anchor_x
            y1 = -self._anchor_y
            x2 = self._x2 + x1 - self._x
            y2 = self._y2 + y1 - self._y
            x3 = self._x3 + x1 - self._x
            y3 = self._y3 + y1 - self._y
            return x1, y1, x2, y2, x3, y3

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def x2(self) -> float:
        """Get/set the X coordinate of the triangle's 2nd vertex."""
        return self._x + self._x2

    @x2.setter
    def x2(self, value: float) -> None:
        self._x2 = value
        self._update_vertices()

    @property
    def y2(self) -> float:
        """Get/set the Y coordinate of the triangle's 2nd vertex."""
        return self._y + self._y2

    @y2.setter
    def y2(self, value: float) -> None:
        self._y2 = value
        self._update_vertices()

    @property
    def x3(self) -> float:
        """Get/set the X coordinate of the triangle's 3rd vertex."""
        return self._x + self._x3

    @x3.setter
    def x3(self, value: float) -> None:
        self._x3 = value
        self._update_vertices()

    @property
    def y3(self) -> float:
        """Get/set the Y value of the triangle's 3rd vertex."""
        return self._y + self._y3

    @y3.setter
    def y3(self, value: float) -> None:
        self._y3 = value
        self._update_vertices()

    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               x2: float | None = None, y2: float | None = None,
               x3: float | None = None, y3: float | None = None,
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
        if x3 is not None:
            self._x3 = x3
            verticles = True
        if y3 is not None:
            self._y3 = y3
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


class Star(ShapeBase):
    def __init__(
            self,
            x: float, y: float,
            outer_radius: float,
            inner_radius: float,
            num_spikes: int,
            rotation: float = 0.0,
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a star.

        The star's anchor point ``(x, y)`` defaults to the on-screen
        center of the star.

        Args:
            x:
                The X coordinate of the star.
            y:
                The Y coordinate of the star.
            outer_radius:
                The desired outer radius of the star.
            inner_radius:
                The desired inner radius of the star.
            num_spikes:
                The desired number of spikes of the star.
            rotation:
                The rotation of the star in degrees. A rotation of 0 degrees
                will result in one spike lining up with the X axis in
                positive direction.
            color:
                The RGB or RGBA color of the star, specified as a
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
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius
        self._num_spikes = num_spikes
        self._rotation = rotation

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            num_spikes * 6,
            blend_src, blend_dest, batch, group, program,
        )

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point((self._x, self._y), point, math.radians(self._rotation))
        center = (self._x - self._anchor_x, self._y - self._anchor_y)
        radius = (self._outer_radius + self._inner_radius) / 2
        return math.dist(center, point) < radius

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            rotation=('f', (self._rotation,) * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y
        r_i = self._inner_radius
        r_o = self._outer_radius

        # get angle covered by each line (= half a spike)
        d_theta = math.pi / self._num_spikes

        # calculate alternating points on outer and outer circles
        points = []
        for i in range(self._num_spikes):
            points.append((x + (r_o * math.cos(2 * i * d_theta)),
                           y + (r_o * math.sin(2 * i * d_theta))))
            points.append((x + (r_i * math.cos((2 * i + 1) * d_theta)),
                           y + (r_i * math.sin((2 * i + 1) * d_theta))))

        # create a list of doubled-up points from the points
        vertices = []
        for i, point in enumerate(points):
            triangle = x, y, *points[i - 1], *point
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def outer_radius(self) -> float:
        """Get/set outer radius of the star."""
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, value: float) -> None:
        self._outer_radius = value
        self._update_vertices()

    @property
    def inner_radius(self) -> float:
        """Get/set the inner radius of the star."""
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value: float) -> None:
        self._inner_radius = value
        self._update_vertices()

    @property
    def num_spikes(self) -> int:
        """Number of spikes of the star."""
        return self._num_spikes

    @num_spikes.setter
    def num_spikes(self, value: int) -> None:
        self._num_spikes = value
        self._update_vertices()
    
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
               outer_radius: float | None = None, inner_radius: float | None = None,
               num_spikes: float | None = None,
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
        
        if outer_radius is not None:
            self._outer_radius = outer_radius
            verticles = True
        if inner_radius is not None:
            self._inner_radius = inner_radius
            verticles = True
        if num_spikes is not None:
            self._num_spikes = num_spikes
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


class Polygon(ShapeBase):
    def __init__(
            self,
            *coordinates: tuple[float, float],
            color: ColorValue = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ) -> None:
        """Create a polygon.

        The polygon's anchor point defaults to the first vertex point.

        Args:
            coordinates:
                The coordinates for each point in the polygon. Each one
                must be able to unpack to a pair of float-like X and Y
                values.
            color:
                The RGB or RGBA color of the polygon, specified as a
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
        # len(self._coordinates) = the number of vertices and sides in the shape.
        self._rotation = 0
        self._coordinates = list(coordinates)
        self._x, self._y = self._coordinates[0]

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255
        super().__init__(
            len(self._coordinates),
            blend_src, blend_dest, batch, group, program,
        )

    def __contains__(self, point: tuple[float, float]) -> bool:
        assert len(point) == 2
        point = _rotate_point(self._coordinates[0], point, math.radians(self._rotation))
        return _point_in_polygon(self._coordinates + [self._coordinates[0]], point)

    def _create_vertex_list(self) -> None:
        vertices = self._get_vertices()
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts, self._draw_mode,
            earcut.earcut(vertices),
            self._batch, self._group,
            position=('f', vertices),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts

        # Adjust all coordinates by the anchor.
        trans_x, trans_y = self._coordinates[0]
        trans_x += self._anchor_x
        trans_y += self._anchor_y
        coords = [[x - trans_x, y - trans_y] for x, y in self._coordinates]

        # Return the flattened coords.
        return earcut.flatten([coords])["vertices"]

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()


    def update(self,
               coordinates: Sequence[tuple[float, float]] | None = None, z: float | None = None,
               anchor_x: float | None = None, anchor_y: float | None = None,
               visible: bool | None = None, rotation: float | None = None,
               color: ColorValue | None = None, opacity: float | None = None) -> None:
        verticles = False
        
        if coordinates is not None:
            x, y =coordinates[0]
            self._x = x
            self._y = y
            self._update_translation()
            
            self._coordinates = list(coordinates)
            verticles = True

        if z is not None:
            self.z = z
        
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
