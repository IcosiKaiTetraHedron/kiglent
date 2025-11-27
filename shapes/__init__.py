"""2D shapes.

This module provides classes for a variety of simplistic 2D shapes,
such as Rectangles, Circles, and Lines. These shapes are made
internally from OpenGL primitives, and provide excellent performance
when drawn as part of a :py:class:`~kiglent.graphics.Batch`.
Convenience methods are provided for positioning, changing color, opacity,
and rotation.
The Python ``in`` operator can be used to check whether a point is inside a shape.
(This is approximated with some shapes, such as Star).

If the shapes in this module don't suit your needs, you have two
options:

.. list-table::
   :header-rows: 1

   * - Your Goals
     - Best Approach

   * - Simple shapes like those here
     - Subclass :py:class:`ShapeBase`

   * - Complex & optimized shapes
     - See :ref:`guide_graphics` to learn about
       the low-level graphics API.


A simple example of drawing shapes::

    import kiglent
    from kiglent import shapes

    window = kiglent.window.Window(960, 540)
    batch = kiglent.graphics.Batch()

    circle = shapes.Circle(700, 150, 100, color=(50, 225, 30), batch=batch)
    square = shapes.Rectangle(200, 200, 200, 200, color=(55, 55, 255), batch=batch)
    rectangle = shapes.Rectangle(250, 300, 400, 200, color=(255, 22, 20), batch=batch)
    rectangle.opacity = 128
    rectangle.rotation = 33
    line = shapes.Line(100, 100, 100, 200, thickness=19, batch=batch)
    line2 = shapes.Line(150, 150, 444, 111, thickness=4, color=(200, 20, 20), batch=batch)
    star = shapes.Star(800, 400, 60, 40, num_spikes=20, color=(255, 255, 0), batch=batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    kiglent.app.run()


.. note:: Some Shapes, such as :py:class:`.Line` and :py:class:`.Triangle`,
          have multiple coordinates.

          These shapes treat their :py:attr:`~ShapeBase.position` as their
          primary coordinate. Changing it or its components (the
          :py:attr:`~ShapeBase.x` or :py:attr:`~ShapeBase.y` properties)
          also moves all secondary coordinates by the same offset from
          the previous :py:attr:`~ShapeBase.position` value. This allows
          you to move these shapes without distorting them.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence, Type

import kiglent
from kiglent.gl import GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_TRIANGLES, glBlendFunc, glDisable, glEnable
from kiglent.graphics import Batch, Group
from kiglent.vector import Vec2

if TYPE_CHECKING:
    from kiglent.graphics.shader import ShaderProgram
    from kiglent.customtypes import ColorValue, Color4

vertex_source = """#version 150 core
    in vec2 position;
    in vec2 translation;
    in vec4 colors;
    in float zposition;

    in float rotation;


    out vec4 vertex_colors;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    mat4 m_rotation = mat4(1.0);
    mat4 m_translate = mat4(1.0);

    void main()
    {
        m_translate[3][0] = translation.x;
        m_translate[3][1] = translation.y;
        m_rotation[0][0] =  cos(-radians(rotation));
        m_rotation[0][1] =  sin(-radians(rotation));
        m_rotation[1][0] = -sin(-radians(rotation));
        m_rotation[1][1] =  cos(-radians(rotation));

        gl_Position = window.projection * window.view * m_translate * m_rotation * vec4(position, zposition, 1.0);
        vertex_colors = colors;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    out vec4 final_color;

    void main()
    {
        final_color = vertex_colors;
        // No GL_ALPHA_TEST in core, use shader to discard.
        if(final_color.a < 0.01){
            discard;
        }
    }
"""


def get_default_shader() -> ShaderProgram:
    return kiglent.gl.current_context.create_program((vertex_source, 'vertex'), (fragment_source, 'fragment'))


def _rotate_point(center: tuple[float, float], point: tuple[float, float], angle: float) -> tuple[float, float]:
    prev_angle = math.atan2(point[1] - center[1], point[0] - center[0])
    now_angle = prev_angle + angle
    r = math.dist(point, center)
    return center[0] + r * math.cos(now_angle), center[1] + r * math.sin(now_angle)


def _get_segment(p0: tuple[float, float] | list[float], p1: tuple[float, float] | list[float],
                 p2: tuple[float, float] | list[float], p3: tuple[float, float] | list[float],
                 thickness: float = 1.0, prev_miter: Vec2 | None = None, prev_scale: Vec2 | None = None) -> tuple[
    Vec2, Vec2, float, float, float, float, float, float, float, float, float, float, float, float]:
    """Computes a line segment between the points p1 and p2.

    If points p0 or p3 are supplied then the segment p1->p2 will have the correct "miter" angle
    for each end respectively.  This returns computed miter and scale values which can be supplied
    to the next call of the method for a minor performance improvement.  If they are not supplied
    then they will be computed.

    Args:
        p0:
            The "previous" point for the segment p1->p2 which is used to compute the "miter"
            angle of the start of the segment.  If None is supplied then the start of the line
            is 90 degrees to the segment p1->p2.
        p1:
            The origin of the segment p1->p2.
        p2:
            The end of the segment p1->p2
        p3:
            The "following" point for the segment p1->p2 which is used to compute the "miter"
            angle to the end of the segment.  If None is supplied then the end of the line is
            90 degrees to the segment p1->p2.
        thickness:
            Thickness of the miter.
        prev_miter:
            The miter value to be used.
        prev_scale:
            The scale value to be used.
    """
    v_np1p2 = Vec2(p2[0] - p1[0], p2[1] - p1[1]).normalize()
    v_normal = Vec2(-v_np1p2.y, v_np1p2.x)

    # Prep the miter vectors to the normal vector in case it is only one segment
    v_miter2 = v_normal
    scale1 = scale2 = thickness / 2.0

    # miter1 is either already computed or the normal
    v_miter1 = v_normal
    if prev_miter and prev_scale:
        v_miter1 = prev_miter
        scale1 = prev_scale
    elif p0:
        # Compute the miter joint vector for the start of the segment
        v_np0p1 = Vec2(p1[0] - p0[0], p1[1] - p0[1]).normalize()
        v_normal_p0p1 = Vec2(-v_np0p1.y, v_np0p1.x)
        # Add the 2 normal vectors and normalize to get miter vector
        v_miter1 = Vec2(v_normal_p0p1.x + v_normal.x, v_normal_p0p1.y + v_normal.y).normalize()
        scale1 = scale1 / math.sin(math.acos(v_np1p2.dot(v_miter1)))

    if p3:
        # Compute the miter joint vector for the end of the segment
        v_np2p3 = Vec2(p3[0] - p2[0], p3[1] - p2[1]).normalize()
        v_normal_p2p3 = Vec2(-v_np2p3.y, v_np2p3.x)
        # Add the 2 normal vectors and normalize to get miter vector
        v_miter2 = Vec2(v_normal_p2p3.x + v_normal.x, v_normal_p2p3.y + v_normal.y).normalize()
        scale2 = scale2 / math.sin(math.acos(v_np2p3.dot(v_miter2)))

    # Quick fix for preventing the scaling factors from getting out of hand
    # with extreme angles.
    scale1 = min(scale1, 2.0 * thickness)
    scale2 = min(scale2, 2.0 * thickness)

    # Make these tuples instead of Vec2 because accessing
    # members of Vec2 is surprisingly slow
    miter1_scaled_p = (v_miter1.x * scale1, v_miter1.y * scale1)
    miter2_scaled_p = (v_miter2.x * scale2, v_miter2.y * scale2)

    v1 = (p1[0] + miter1_scaled_p[0], p1[1] + miter1_scaled_p[1])
    v2 = (p2[0] + miter2_scaled_p[0], p2[1] + miter2_scaled_p[1])
    v3 = (p1[0] - miter1_scaled_p[0], p1[1] - miter1_scaled_p[1])
    v4 = (p2[0] + miter2_scaled_p[0], p2[1] + miter2_scaled_p[1])
    v5 = (p2[0] - miter2_scaled_p[0], p2[1] - miter2_scaled_p[1])
    v6 = (p1[0] - miter1_scaled_p[0], p1[1] - miter1_scaled_p[1])

    return v_miter2, scale2, v1[0], v1[1], v2[0], v2[1], v3[0], v3[1], v4[0], v4[1], v5[0], v5[1], v6[0], v6[1]


class _ShapeGroup(Group):
    """Shared Shape rendering Group.

    The group is automatically coalesced with other shape groups
    sharing the same parent group and blend parameters.
    """

    def __init__(self, blend_src: int, blend_dest: int, program: ShaderProgram, parent: Group | None = None) -> None:
        """Create a Shape group.

        The group is created internally. Usually you do not
        need to explicitly create it.

        Args:
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            program:
                The ShaderProgram to use.
            parent:
                Optional parent group.
        """
        super().__init__(parent=parent)
        self.program = program
        self.blend_src = blend_src
        self.blend_dest = blend_dest

    def set_state(self) -> None:
        self.program.bind()
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self) -> None:
        glDisable(GL_BLEND)
        self.program.unbind()

    def __eq__(self, other: Group | _ShapeGroup) -> None:
        return (other.__class__ is self.__class__ and
                self.program == other.program and
                self.parent == other.parent and
                self.blend_src == other.blend_src and
                self.blend_dest == other.blend_dest)

    def __hash__(self) -> int:
        return hash((self.program, self.parent, self.blend_src, self.blend_dest))


class ShapeBase(ABC):
    """Base class for all shape objects.

    A number of default shapes are provided in this module. Curves are
    approximated using multiple vertices.

    If you need shapes or functionality not provided in this module,
    you can write your own custom subclass of ``ShapeBase`` by using
    the provided shapes as reference.
    """

    # _rgba and any class attribute set to None is untyped because
    # doing so doesn't require None-handling from some type checkers.
    _rgba: Color4 = (255, 255, 255, 255)
    _rotation: float = 0.0
    _visible: bool = True
    _x: float = 0.0
    _y: float = 0.0
    _z: float = 0.0
    _anchor_x: float = 0.0
    _anchor_y: float = 0.0
    _batch: Batch | None = None
    _group: _ShapeGroup | Group | None = None
    _num_verts: int = 0
    _user_group: Group | None = None
    _vertex_list = None
    _draw_mode: int = GL_TRIANGLES
    group_class: Type[Group] = _ShapeGroup

    def __init__(self,
                 vertex_count: int,
                 blend_src: int = GL_SRC_ALPHA,
                 blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
                 batch: Batch | None = None,
                 group: Group | None = None,
                 program: ShaderProgram | None = None,
                 ) -> None:
        """Initialize attributes that all Shape object's require.

        Args:
            vertex_count:
                The amount of vertices this Shape object has.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch object.
            group:
                Optional group object.
            program:
                Optional ShaderProgram object.
        """
        self._num_verts = vertex_count
        self._blend_src = blend_src
        self._blend_dest = blend_dest
        self._batch = batch
        self._user_group = group
        self._program = program or get_default_shader()
        self._group = self.get_shape_group()
        self._create_vertex_list()

    def __del__(self) -> None:
        if self._vertex_list is not None:
            self._vertex_list.delete()
            self._vertex_list = None

    def __contains__(self, point: tuple[float, float]) -> bool:
        """Test whether a point is inside a shape."""
        raise NotImplementedError(f"The `in` operator is not supported for {self.__class__.__name__}")

    def get_shape_group(self) -> _ShapeGroup | Group:
        """Creates and returns a group to be used to render the shape.

        This is used internally to create a consolidated group for rendering.

        .. note:: This is for advanced usage. This is a group automatically created internally as a child of ``group``,
                  and does not need to be modified unless the parameters of your custom group changes.

        .. versionadded:: 2.0.16
        """
        return self.group_class(self._blend_src, self._blend_dest, self._program, self._user_group)

    def _update_color(self) -> None:
        """Send the new colors for each vertex to the GPU.

        This method must set the contents of `self._vertex_list.colors`
        using a list or tuple that contains the RGBA color components
        for each vertex in the shape. This is usually done by repeating
        `self._rgba` for each vertex.
        """
        self._vertex_list.colors[:] = self._rgba * self._num_verts

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (self._x, self._y) * self._num_verts

    def _create_vertex_list(self) -> None:
        """Build internal vertex list.

        This method must create a vertex list and assign it to
        `self._vertex_list`. It is advisable to use it
        during `__init__` and to then update the vertices accordingly
        with `self._update_vertices`.

        While it is not mandatory to implement it, some properties (
        namely `batch` and `group`) rely on this method to properly
        recreate the vertex list.
        """
        raise NotImplementedError('_create_vertex_list must be defined in order to use group or batch properties')

    @abstractmethod
    def _update_vertices(self) -> None:
        """Generate up-to-date vertex positions & send them to the GPU.

        This method must set the contents of `self._vertex_list.vertices`
        using a list or tuple that contains the new vertex coordinates for
        each vertex in the shape. See the `ShapeBase` subclasses in this
        module for examples of how to do this.
        """
        raise NotImplementedError("_update_vertices must be defined for every ShapeBase subclass")
    
    @property
    def blend_mode(self) -> tuple[int, int]:
        """The current blend mode applied to this shape.

        .. note:: Changing this can be an expensive operation as it involves a group creation and transfer.
        """
        return self._blend_src, self._blend_dest

    @blend_mode.setter
    def blend_mode(self, modes: tuple[int, int]) -> None:
        src, dst = modes
        if src == self._blend_src and dst == self._blend_dest:
            return

        self._blend_src = src
        self._blend_dest = dst

        self._group = self.get_shape_group()
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, self._draw_mode, self._group, self._batch)
        else:
            self._vertex_list.delete()
            self._create_vertex_list()

    @property
    def program(self) -> ShaderProgram:
        """The current shader program.

        .. note:: Changing this can be an expensive operation as it involves a group creation and transfer.
        """
        return self._program

    @program.setter
    def program(self, program: ShaderProgram) -> None:
        if self._program == program:
            return
        self._program = program
        self._group = self.get_shape_group()

        if (self._batch and
                self._batch.update_shader(self._vertex_list, GL_TRIANGLES, self._group, program)):
            # Exit early if changing domain is not needed.
            return

        # Recreate vertex list.
        self._vertex_list.delete()
        self._create_vertex_list()

    @property
    def rotation(self) -> float:
        """Get/set the shape's clockwise rotation in degrees.

        All shapes rotate around their :attr:`.anchor_position`.
        For most shapes, this defaults to both:

        * The shape's first vertex of the shape
        * The lower left corner

        Shapes with a ``radius`` property rotate around the
        point the radius is measured from. This will be either
        their center or the center of the circle they're cut from:

        These shapes rotate around their center:

        * :py:class:`.Circle`
        * :py:class:`.Ellipse`
        * :py:class:`.Star`

        These shapes rotate around the point of their angles:

        * :py:class:`.Arc`
        * :py:class:`.Sector`

        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: float) -> None:
        self._rotation = rotation
        self._vertex_list.rotation[:] = (rotation,) * self._num_verts

    def draw(self) -> None:
        """Debug method to draw a single shape at its current position.

        .. warning:: Avoid this inefficient method for everyday use!

                     Regular drawing should add shapes to a :py:class:`Batch`
                     and call its :py:meth:`~Batch.draw` method.

        """
        self._group.set_state_recursive()
        self._vertex_list.draw(self._draw_mode)
        self._group.unset_state_recursive()

    def delete(self) -> None:
        """Force immediate removal of the shape from video memory.

        You should usually call this whenever you no longer need the shape.
        Otherwise, Python may call the finalizer of the shape instance only
        some time after the shape has fallen out of scope, and the shape's video
        memory will not be freed until the finalizer is eventually called by
        garbage collection.

        Implementing manual garbage collection may satisfy the same concern
        without using the current method, but is a very advanced technique.
        """
        if self._vertex_list is not None:
            self._vertex_list.delete()
            self._vertex_list = None

    @property
    def x(self) -> float:
        """Get/set the X coordinate of the shape's :py:attr:`.position`.

        #. To update both :py:attr:`.x` and :py:attr:`.y`, use
           :attr:`.position` instead.
        #. Shapes may vary slightly in how they use :py:attr:`.position`

        See :py:attr:`.position` to learn more.
        """
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value
        self._update_translation()

    @property
    def y(self) -> float:
        """Get/set the Y coordinate of the shape's :py:attr:`.position`.

        This property has the following pitfalls:

        #. To update both :py:attr:`.x` and :py:attr:`.y`, use
           :py:attr:`.position` instead.
        #. Shapes may vary slightly in how they use :py:attr:`.position`

        See :attr:`.position` to learn more.
        """
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value
        self._update_translation()

    @property
    def z(self) -> float:
        """Get/set the Z coordinate of the shape.

        You must enable depth testing for this to have any effect.
        For example: create a custom parent :py:class:`~kiglent.graphics.Group`
        that enables and disables depth testing, and use that with all of
        your shapes that will have non-0 Z values.
        """
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._vertex_list.zposition = (value,) * self._num_verts

    @property
    def position(self) -> tuple[float, float]:
        """Get/set the ``(x, y)`` coordinates of the shape.

        .. tip:: This is more efficient than setting :py:attr:`.x`
                 and :py:attr:`.y` separately!

        All shapes default to rotating around their position. However,
        the way they do so varies.

        Shapes with a ``radius`` property will use this as their
        center:

        * :py:class:`.Circle`
        * :py:class:`.Ellipse`
        * :py:class:`.Arc`
        * :py:class:`.Sector`
        * :py:class:`.Star`

        Others default to using it as their lower left corner.
        """
        return self._x, self._y

    @position.setter
    def position(self, values: tuple[float, float]) -> None:
        self._x, self._y = values
        self._update_translation()

    @property
    def anchor_x(self) -> float:
        """Get/set the X coordinate of the anchor point.

        If you need to set both this and :py:attr:`.anchor_x`, use
        :py:attr:`.anchor_position` instead.
        """
        return self._anchor_x

    @anchor_x.setter
    def anchor_x(self, value: float) -> None:
        self._anchor_x = value
        self._update_vertices()

    @property
    def anchor_y(self) -> float:
        """Get/set the Y coordinate of the anchor point.

        If you need to set both this and :py:attr:`.anchor_x`, use
        :py:attr:`.anchor_position` instead.
        """
        return self._anchor_y

    @anchor_y.setter
    def anchor_y(self, value: float) -> None:
        self._anchor_y = value
        self._update_vertices()

    @property
    def anchor_position(self) -> tuple[float, float]:
        """Get/set the anchor's ``(x, y)`` offset from :py:attr:`.position`.

        This defines the point a shape rotates around. By default, it is
        ``(0.0, 0.0)``. However:

        * Its behavior may vary between shape classes.
        * On many shapes, you can set the anchor or its components
          (:py:attr:`.anchor_x` and :attr:`.anchor_y`) to custom values.

        Since all anchor updates recalculate a shape's vertices on the
        CPU, this property is faster than updating :py:attr:`.anchor_x` and
        :py:attr:`.anchor_y` separately.
        """
        return self._anchor_x, self._anchor_y

    @anchor_position.setter
    def anchor_position(self, values: tuple[float, float]) -> None:
        self._anchor_x, self._anchor_y = values
        self._update_vertices()

    @property
    def color(self) -> Color4:
        """Get/set the shape's color.

        The color may set to:

        - An RGBA tuple of integers ``(red, green, blue, alpha)``
        - An RGB tuple of integers ``(red, green, blue)``

        If an RGB color is set, the current alpha will be preserved.
        Otherwise, the new alpha value will be used for the shape. Each
        color component must be in the range 0 (dark) to 255 (saturated).
        """
        return self._rgba

    @color.setter
    def color(self, values: ColorValue) -> None:
        r, g, b, *a = values

        if a:
            self._rgba = r, g, b, a[0]
        else:
            self._rgba = r, g, b, self._rgba[3]

        self._update_color()

    @property
    def opacity(self) -> int:
        """Get/set the blend opacity of the shape.

        .. tip:: To toggle visibility on/off, :py:attr:`.visible` may be
                 more efficient!

        Opacity is implemented as the alpha component of a shape's
        :py:attr:`.color`. When part of a group with a default blend
        mode of ``(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)``, opacities
        below ``255`` draw with fractional opacity over the background:

        .. list-table:: Example Values & Effects
           :header-rows: 1

           * - Opacity
             - Effect

           * - ``255`` (Default)
             - Shape is fully opaque

           * - ``128``
             - Shape looks translucent

           * - ``0``
             - Invisible

        """
        return self._rgba[3]

    @opacity.setter
    def opacity(self, value: int) -> None:
        self._rgba = (*self._rgba[:3], value)
        self._update_color()

    @property
    def visible(self) -> bool:
        """Get/set whether the shape will be drawn at all.

        For absolute showing / hiding, this is
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value
        self._update_vertices()

    @property
    def group(self) -> Group | None:
        """Get/set the shape's :class:`Group`.

        You can migrate a shape from one group to another by setting
        this property. Note that it can be an expensive (slow) operation.

        If :py:attr:`.batch` isn't ``None``, setting this property will
        also trigger a batch migration.
        """
        return self._user_group

    @group.setter
    def group(self, group: Group) -> None:
        if self._user_group == group:
            return
        self._user_group = group
        self._group = self.get_shape_group()
        if self._batch:
            self._batch.migrate(self._vertex_list, self._draw_mode, self._group, self._batch)

    @property
    def batch(self) -> Batch | None:
        """Get/set the :py:class:`Batch` for this shape.

        .. warning:: Setting this to ``None`` currently breaks things!

                     Known issues include :py:attr:`.group` breaking.

        You can migrate a shape from one batch to another by setting
        this property, but it can be an expensive (slow) operation.
        """
        return self._batch

    @batch.setter
    def batch(self, batch: Batch | None) -> None:
        if self._batch == batch:
            return

        if batch is not None and self._batch is not None:
            self._batch.migrate(self._vertex_list, self._draw_mode, self._group, batch)
            self._batch = batch
        else:
            self._vertex_list.delete()
            self._batch = batch
            self._create_vertex_list()
    
    
    def update(self,
               x: float | None = None, y: float | None = None, z: float | None = None,
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


from .rectangle import *
from .circle import *
from .polygon import *
from .lines import *
from .curves import *


__all__ = ['Rectangle', 'BorderedRectangle', 'RoundedRectangle', 'Frame',
           'Rect', 'BorderedRect', 'RectBordered', 'RoundedRect', 'RectRounded', 'Box',
           'Circle', 'Ellipse', 'Sector', 'Triangle', 'Star', 'Polygon',
           'Line', 'MultiLine', 'Lines', 'Arc', 'BezierCurve', 'ShapeBase']

