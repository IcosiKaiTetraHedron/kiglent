from __future__ import annotations

import weakref
import math as _math
from typing import TYPE_CHECKING

from kiglent import window as _window
from kiglent.vector import Vec3
from kiglent.matrix import Mat4

if TYPE_CHECKING:
    from kiglent.graphics import Batch


__all__ = ['Group', 'ShaderGroup', 'TextureGroup', 'TranslationGroup', 'ScaleGroup', 'RotationGroup']


class Group:
    """Group of common OpenGL state.

    ``Group`` provides extra control over how drawables are handled within a
    ``Batch``. When a batch draws a drawable, it ensures its group's state is set;
    this can include binding textures, shaders, or setting any other parameters.
    It also sorts the groups before drawing.

    In the following example, the background sprite is guaranteed to be drawn
    before the car and the boat::

        batch = kiglent.graphics.Batch()
        background = kiglent.graphics.Group(order=0)
        foreground = kiglent.graphics.Group(order=1)

        background = kiglent.sprite.Sprite(background_image, batch=batch, group=background)
        car = kiglent.sprite.Sprite(car_image, batch=batch, group=foreground)
        boat = kiglent.sprite.Sprite(boat_image, batch=batch, group=foreground)

        def on_draw():
            batch.draw()
    """

    def __init__(self, order: int = 0, parent: Group | None = None) -> None:
        """Initialize a rendering group.

        Args:
            order:
                Set the order to render above or below other Groups.
                Lower orders are drawn first.
            parent:
                Group to contain this Group; its state will be set before this Group's state.
        """
        self._order = order
        self.parent = parent
        self._visible = True
        self._assigned_batches = weakref.WeakSet()

    @property
    def order(self) -> int:
        """Rendering order of this group compared to others.

        Lower numbers are drawn first.
        """
        return self._order

    @property
    def visible(self) -> bool:
        """Visibility of the group in the rendering pipeline.

        Determines whether this Group is visible in any of the Batches
        it is assigned to. If ``False``, objects in this Group will not
        be rendered.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

        for batch in self._assigned_batches:
            batch.invalidate()

    @property
    def batches(self) -> tuple[Batch, ...]:
        """Which graphics Batches this Group is a part of.

        Read Only.
        """
        return tuple(self._assigned_batches)

    def __lt__(self, other: Group) -> bool:
        return self._order < other.order

    def __eq__(self, other: Group) -> bool:
        """Comparison function used to determine if another Group is providing the same state.

        When the same state is determined, those groups will be consolidated into one draw call.

        If subclassing, then care must be taken to ensure this function can compare to another of the same group.

        :see: ``__hash__`` function, both must be implemented.
        """
        return (self.__class__ is other.__class__ and
                self._order == other.order and
                self.parent == other.parent)

    def __hash__(self) -> int:
        """This is an immutable return to establish the permanent identity of the object.

        This is used by Python with ``__eq__`` to determine if something is unique.

        For simplicity, the hash should be a tuple containing your unique identifiers of your Group.

        By default, this is (``order``, ``parent``).

        :see: ``__eq__`` function, both must be implemented.
        """
        return hash((self._order, self.parent))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(order={self._order})"

    def set_state(self) -> None:
        """Apply the OpenGL state change.

        The default implementation does nothing.
        """

    def unset_state(self) -> None:
        """Repeal the OpenGL state change.

        The default implementation does nothing.
        """

    def set_state_recursive(self) -> None:
        """Set this group and its ancestry.

        Call this method if you are using a group in isolation: the
        parent groups will be called in top-down order, with this class's
        ``set`` being called last.
        """
        if self.parent:
            self.parent.set_state_recursive()
        self.set_state()

    def unset_state_recursive(self) -> None:
        """Unset this group and its ancestry.

        The inverse of ``set_state_recursive``.
        """
        self.unset_state()
        if self.parent:
            self.parent.unset_state_recursive()


class ShaderGroup(Group):
    """A group that enables and binds a ShaderProgram."""

    def __init__(self, program: ShaderProgram, order: int = 0, parent: Group | None = None) -> None:  # noqa: D107
        super().__init__(order, parent)
        self.program = program

    def set_state(self) -> None:
        self.program.use()

    def unset_state(self) -> None:
        self.program.stop()

    def __eq__(self, other: ShaderGroup) -> bool:
        return (self.__class__ is other.__class__ and
                self._order == other.order and
                self.program == other.program and
                self.parent == other.parent)

    def __hash__(self) -> int:
        return hash((self._order, self.parent, self.program))


class TextureGroup(Group):
    """A group that enables and binds a texture.

    TextureGroups are equal if their textures' targets and names are equal.
    """

    def __init__(self, texture: kiglent.image.Texture, order: int = 0, parent: Group | None = None) -> None:
        """Create a texture group.

        Args:
            texture:
                Texture to bind.
            order:
                Change the order to render above or below other Groups.
            parent:
                Parent group.
        """
        super().__init__(order, parent)
        self.texture = texture

    def set_state(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture.target, self.texture.id)

    def __hash__(self) -> int:
        return hash((self.texture.target, self.texture.id, self.order, self.parent))

    def __eq__(self, other: TextureGroup) -> bool:
        return (self.__class__ is other.__class__ and
                self.texture.target == other.texture.target and
                self.texture.id == other.texture.id and
                self.order == other.order and
                self.parent == other.parent)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(order={self._order}, id={self.texture.id})'


class TranslationGroup(Group):
    window: _window.BaseWindow
    
    _x: float = 0.0
    _y: float = 0.0
    _vec3: tuple[float, float, float] | Vec3
    _projection: Mat4
    def __init__(self,
                 order: int = 0, parent: Group | None = None,
                 x: float = 0.0, y: float = 0.0,
                 window: _window.BaseWindow | None = None) -> None:
        super().__init__(order, parent)
        self._x = x
        self._y = y
        self._vec3 = (x, y, 0.0)
        if window is None:
            window = _window.get_current_window()
        self.window = window
        self._projection = window.projection

    @property
    def x(self) -> float:
        return self._x
    @x.setter
    def x(self, x: float) -> None:
        self._x = x
        self._vec3 = (x, self._y, 0.0)

    @property
    def y(self) -> float:
        return self._y
    @y.setter
    def y(self, y: float) -> None:
        self._y = y
        self._vec3 = (self._x, y, 0.0)

    def set_state(self) -> None:
        projection = self.window.projection
        self._projection = projection
        self.window.projection = projection.translate(self._vec3)

    def unset_state(self) -> None:
        self.window.projection = self._projection

    def __eq__(self, other: TranslationGroup) -> bool:
        return (self.__class__ is other.__class__ and
                self._order == other.order and
                self.window == other.window and
                self.parent == other.parent)

    def __hash__(self) -> int:
        return hash((self._order, self.parent, self.window))
    
class ScaleGroup(Group):
    window: _window.BaseWindow
    
    _scale_x: float = 0.0
    _scale_y: float = 0.0
    _vec3: tuple[float, float, float] | Vec3
    _projection: Mat4
    def __init__(self,
                 order: int = 0, parent: Group | None = None,
                 scale_x: float = 1.0, scale_y: float = 1.0,
                 window: _window.BaseWindow | None = None) -> None:
        super().__init__(order, parent)
        self._scale_x = scale_x
        self._scale_y = scale_y
        self._vec3 = (scale_x, scale_y, 1.0)
        if window is None:
            window = _window.get_current_window()
        self.window = window
        self._projection = window.projection

    @property
    def scale_x(self) -> float:
        return self._scale_x
    @scale_x.setter
    def scale_x(self, scale_x: float) -> None:
        self._scale_x = scale_x
        self._vec3 = (scale_x, self._scale_y, 1.0)

    @property
    def scale_y(self) -> float:
        return self._scale_y
    @scale_y.setter
    def scale_y(self, scale_y: float) -> None:
        self._scale_y = scale_y
        self._vec3 = (self._scale_x, scale_y, 1.0)

    def set_state(self) -> None:
        projection = self.window.projection
        self._projection = projection
        self.window.projection = projection.scale(self._vec3)

    def unset_state(self) -> None:
        self.window.projection = self._projection

    def __eq__(self, other: TranslationGroup) -> bool:
        return (self.__class__ is other.__class__ and
                self._order == other.order and
                self.window == other.window and
                self.parent == other.parent)

    def __hash__(self) -> int:
        return hash((self._order, self.parent, self.window))


class RotationGroup(Group):
    window: _window.BaseWindow
    
    _rotation: float = 0.0
    _projection: Mat4
    def __init__(self,
                 order: int = 0, parent: Group | None = None,
                 rotation: float = 0.0,
                 window: _window.BaseWindow | None = None) -> None:
        super().__init__(order, parent)
        self._rotation = rotation
        if window is None:
            window = _window.get_current_window()
        self.window = window
        self._projection = window.projection

    @property
    def rotation(self) -> float:
        return self._rotation
    @rotation.setter
    def rotation(self, rotation: float) -> None:
        self._rotation = rotation

    def set_state(self) -> None:
        projection = self.window.projection
        self._projection = projection
        self.window.projection = projection.rotate_z(self._rotation)

    def unset_state(self) -> None:
        self.window.projection = self._projection

    def __eq__(self, other: TranslationGroup) -> bool:
        return (self.__class__ is other.__class__ and
                self._order == other.order and
                self.window == other.window and
                self.parent == other.parent)

    def __hash__(self) -> int:
        return hash((self._order, self.parent, self.window))


