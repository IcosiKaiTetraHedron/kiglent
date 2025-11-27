"""Vector math.

This module provides Vector objects, including Vec2, Vec3 and Vec4.
Most common vector operations aresupported.
Helper methods are included for rotating, scaling, and transforming.

All objects are immutable and hashable.
"""

from __future__ import annotations

import math as _math
import typing as _typing


def clamp(num: float, minimum: float, maximum: float) -> float:
    """Clamp a value between a minimum and maximum limit."""
    if num < minimum:
        return minimum
    if num > maximum:
        return maximum
    return num


class Vec2(_typing.NamedTuple):
    """A two-dimensional vector represented as an X Y coordinate pair.

    `Vec2` is an immutable 2D Vector, including most common
    operators. As an immutable type, all operations return a new object.

    .. note:: The Python ``len`` operator returns the number of elements in
              the vector. For the vector length, use the `length()` method.

    .. note:: Python's :py:func:`sum` requires the first item to be a ``Vec2``.

              After that, you can mix ``Vec2``-like :py:class:`tuple`
              and ``Vec2`` instances freely in the iterable.

              If you do not, you will see a :py:class:`TypeError` about being
              unable to add a :py:class:`tuple` and a :py:class:`int`.

    """

    x: float = 0.0
    y: float = 0.0

    def __bool__(self):
        return self.x != 0.0 or self.y != 0.0

    def __add__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return Vec2(
                self[0] + other[0], self[1] + other[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] + other, self[1] + other  # type: ignore
            )

    def __radd__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return self.__add__(other)
        except TypeError as err:
            if other == 0:  # Required for functionality with sum()
                return self
            raise err

    def __sub__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return Vec2(
                self[0] - other[0], self[1] - other[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] - other, self[1] - other  # type: ignore
            )

    def __rsub__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return Vec2(
                other[0] - self[0], other[1] - self[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                other - self[0], other - self[1]  # type: ignore
            )

    def __mul__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                self[0] * scalar[0], self[1] * scalar[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] * scalar, self[1] * scalar  # type: ignore
            )

    def __rmul__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                self[0] * scalar[0], self[1] * scalar[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] * scalar, self[1] * scalar  # type: ignore
            )

    def __truediv__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                self[0] / scalar[0], self[1] / scalar[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] / scalar, self[1] / scalar  # type: ignore
            )

    def __rtruediv__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                scalar[0] / self[0], scalar[1] / self[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                scalar / self[0], scalar / self[1]  # type: ignore
            )

    def __floordiv__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                self.x // scalar[0], self.y // scalar[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] // scalar, self[1] // scalar  # type: ignore
            )

    def __rfloordiv__(self, scalar: float | Vec2 | tuple[float, float]) -> Vec2:
        try:
            return Vec2(
                scalar[0] // self[0], scalar[1] // self[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                scalar // self[0], scalar // self[1]  # type: ignore
            )

    def __abs__(self) -> Vec2:
        return Vec2(abs(self[0]), abs(self[1]))

    def __neg__(self) -> Vec2:
        return Vec2(-self[0], -self[1])

    def __round__(self, n_digits: int | None = None) -> Vec2:
        return Vec2(*(round(v, n_digits) for v in self))

    def __ceil__(self) -> Vec2:
        return Vec2(_math.ceil(self[0]), _math.ceil(self[1]))

    def __floor__(self) -> Vec2:
        return Vec2(_math.floor(self[0]), _math.floor(self[1]))

    def __trunc__(self) -> Vec2:
        return Vec2(_math.trunc(self[0]), _math.trunc(self[1]))

    def __mod__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return Vec2(
                self[0] % other[0], self[1] % other[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] % other, self[1] % other  # type: ignore
            )

    def __pow__(self, other: Vec2 | tuple[float, float] | float) -> Vec2:
        try:
            return Vec2(
                self[0] ** other[0], self[1] ** other[1]  # type: ignore
            )
        except TypeError:
            return Vec2(
                self[0] ** other, self[1] ** other  # type: ignore
            )

    def __lt__(self, other: tuple[float, float]) -> bool:
        return self[0] ** 2 + self[1] ** 2 < other[0] ** 2 + other[1] ** 2

    @staticmethod
    def from_heading(heading: float, length: float = 1.0) -> Vec2:
        """Create a new vector from the given heading and length.

        Args:
          heading: The desired heading, in radians
          length: The desired length of the vector
        """
        return Vec2(length * _math.cos(heading), length * _math.sin(heading))

    @staticmethod
    def from_polar(angle: float, length: float = 1.0) -> Vec2:
        """Create a new vector from the given polar coordinates.

        Args:
          angle: The angle, in radians.
          length: The desired length
        """
        return Vec2(length * _math.cos(angle), length * _math.sin(angle))

    def length(self) -> float:
        """Calculate the length of the vector: ``sqrt(x ** 2 + y ** 2)``."""
        return _math.sqrt(self[0] ** 2 + self[1] ** 2)

    def heading(self) -> float:
        """Calculate the heading of the vector in radians.

        Shortcut for `atan2(y, x)` meaning it returns a value between
        -pi and pi. ``Vec2(1, 0)`` will have a heading of 0. Counter-clockwise
        is positive moving towards pi, and clockwise is negative moving towards -pi.
        """
        return _math.atan2(self[1], self[0])

    def length_squared(self) -> float:
        """Calculate the squared length of the vector.

        This is simply shortcut for `x ** 2 + y ** 2` and can be used
        for faster comparisons without the need for a square root.
        """
        return self[0] ** 2.0 + self[1] ** 2.0

    def lerp(self, other: Vec2 | tuple[float, float], amount: float) -> Vec2:
        """Create a new Vec2 linearly interpolated between this vector and another Vec2.

        The equivalent in GLSL is `mix`.

        Args:
          other: Another Vec2 instance.
          amount: The amount of interpolation between this vector, and the other
                  vector. This should be a value between 0.0 and 1.0. For example:
                  0.5 is the midway point between both vectors.
        """
        return Vec2(self[0] + (amount * (other[0] - self.x)), self[1] + (amount * (other[1] - self[1])))

    def step(self, edge: Vec2 | tuple[float, float]) -> Vec2:
        """A step function that returns 0.0 for a component if it is less than the edge, and 1.0 otherwise.

        This can be used enable and disable some behavior based on a condition.

        Example::

            # First component is less than 1.0, second component is greater than 1.0
            Vec2(0.5, 1.5).step((1.0, 1.0))
            Vec2(1.0, 0.0)

        Args:
            edge: A Vec2 instance.
        """
        return Vec2(0.0 if self[0] < edge[0] else 1.0, 0.0 if self[1] < edge[1] else 1.0)

    def reflect(self, vector: Vec2 | tuple[float, float]) -> Vec2:
        """Create a new Vec2 reflected (ricochet) from the given normalized vector.

        Args:
            vector: A normalized Vec2 or Vec2-like tuple.
        """
        # Less unrolled equivalent of code below:
        #  return self - vector * 2 * vector.dot(self)
        twice_dot_value = self.dot(vector) * 2
        return Vec2(
            self[0] - twice_dot_value * vector[0],
            self[1] - twice_dot_value * vector[1]
        )

    def rotate(self, angle: float) -> Vec2:
        """Create a new vector rotated by the angle. The length remains unchanged.

        Args:
            angle: The desired angle, in radians.
        """
        s = _math.sin(angle)
        c = _math.cos(angle)
        return Vec2(c * self[0] - s * self[1], s * self[0] + c * self[1])

    def distance(self, other: Vec2 | tuple[int, int]) -> float:
        """Calculate the distance between this vector and another vector.

        Args:
            other: The point to calculate the distance to.
        """
        return _math.sqrt(((other[0] - self[0]) ** 2) + ((other[1] - self[1]) ** 2))

    def normalize(self) -> Vec2:
        """Return a normalized version of the vector.

        This simply means the vector will have a length of 1.0. If the vector
        has a length of 0, the original vector will be returned.
        """
        if d := _math.sqrt(self[0] ** 2 + self[1] ** 2):
            return Vec2(self[0] / d, self[1] / d)
        return self

    if _typing.TYPE_CHECKING:
        @_typing.overload
        def clamp(self, min_val: float, max_val: float) -> Vec2:
            ...

        @_typing.overload
        def clamp(self, min_val: Vec2 | tuple[float, float], max_val: Vec2 | tuple[float, float]) -> Vec2:
            ...

        # -- Begin revert if perf-impacting block --
        @_typing.overload
        def clamp(self, min_val: Vec2 | tuple[float, float], max_val: float) -> Vec2:
            ...

        @_typing.overload
        def clamp(self, min_val: float, max_val: Vec2 | tuple[float, float]) -> Vec2:
            ...
        # -- End revert if perf-impacting block --

    def clamp(self, min_val: Vec2 | tuple[float, float] | float, max_val: Vec2 | tuple[float, float] | float) -> Vec2:
        """Restrict the value of the X and Y components of the vector to be within the given values.

        If a single value is provided, it will be used for both X and Y.
        If a tuple or Vec2 is provided, the first value will be used for X and the second for Y.

        Args:
            min_val: The minimum value(s)
            max_val: The maximum value(s)
        """
        try:
            min_x, min_y = min_val[0], min_val[1]  # type: ignore
        except TypeError:
            min_x = min_val
            min_y = min_val
        try:
            max_x, max_y = max_val[0], max_val[1]  # type: ignore
        except TypeError:
            max_x = max_val
            max_y = max_val

        return Vec2(
            clamp(self[0], min_x, max_x), clamp(self[1], min_y, max_y),  # type: ignore
        )

    def dot(self, other: Vec2 | tuple[float, float]) -> float:
        """Calculate the dot product of this vector and another 2D vector."""
        return self[0] * other[0] + self[1] * other[1]

    def index(self, *args: _typing.Any) -> int:
        raise NotImplementedError("Vec types can be indexed directly.")

    def __getattr__(self, attrs: str) -> Vec2 | Vec3 | Vec4:
        try:
            # Allow swizzled getting of attrs
            vec_class = {2: Vec2, 3: Vec3, 4: Vec4}[len(attrs)]
            return vec_class(*(self['xy'.index(c)] for c in attrs))
        except (ValueError, KeyError, TypeError) as err:
            msg = f"'Vec2' has no attribute: '{attrs}'."
            raise AttributeError(msg) from err


class Vec3(_typing.NamedTuple):
    """A three-dimensional vector represented as X Y Z coordinates.

    `Vec3` is an immutable 3D Vector, including most common operators.
    As an immutable type, all operations return a new object.

    .. note:: The Python ``len`` operator returns the number of elements in
              the vector. For the vector length, use the `length()` method.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __bool__(self):
        return self.x != 0.0 or self.y != 0.0 or self.z != 0.0

    def __add__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return Vec3(
                self[0] + other[0], self[1] + other[1], self[2] + other[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] + other, self[1] + other, self[2] + other  # type: ignore
            )

    def __radd__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return self.__add__(_typing.cast(Vec3, other))
        except TypeError as err:
            if other == 0:  # Required for functionality with sum()
                return self
            raise err

    def __sub__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return Vec3(
                self[0] - other[0], self[1] - other[1], self[2] - other[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] - other, self[1] - other, self[2] - other  # type: ignore
            )

    def __rsub__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return Vec3(
                other[0] - self[0], other[1] - self[1], other[2] - self[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                other - self[0], other - self[1], other - self[2]  # type: ignore
            )

    def __mul__(self, scalar: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                self[0] * scalar[0], self[1] * scalar[1], self[2] * scalar[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] * scalar, self[1] * scalar, self[2] * scalar  # type: ignore
            )

    def __rmul__(self, scalar: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                self[0] * scalar[0], self[1] * scalar[1], self[2] * scalar[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] * scalar, self[1] * scalar, self[2] * scalar  # type: ignore
            )

    def __truediv__(self, scalar: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                self[0] / scalar[0], self[1] / scalar[1], self[2] / scalar[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] / scalar, self[1] / scalar, self[2] / scalar  # type: ignore
            )

    def __rtruediv__(self, other: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                other[0] / self[0], other[1] / self[1], other[2] / self[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                other / self[0], other / self[1], other / self[2]  # type: ignore
            )

    def __floordiv__(self, other: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                self[0] // other[0], self[1] // other[1], self[2] // other[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] // other, self[1] // other, self[2] // other  # type: ignore
            )

    def __rfloordiv__(self, other: float | Vec3 | tuple[float, float, float]) -> Vec3:
        try:
            return Vec3(
                other[0] // self[0], other[1] // self[1], other[2] // self[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                other // self[0], other // self[1], other // self[2]  # type: ignore
            )

    def __abs__(self) -> Vec3:
        return Vec3(abs(self[0]), abs(self[1]), abs(self[2]))

    def __neg__(self) -> Vec3:
        return Vec3(-self[0], -self[1], -self[2])

    def __round__(self, n_digits: int | None = None) -> Vec3:
        return Vec3(*(round(v, n_digits) for v in self))

    def __ceil__(self) -> Vec3:
        return Vec3(_math.ceil(self[0]), _math.ceil(self[1]), _math.ceil(self[2]))

    def __floor__(self) -> Vec3:
        return Vec3(_math.floor(self[0]), _math.floor(self[1]), _math.floor(self[2]))

    def __trunc__(self) -> Vec3:
        return Vec3(_math.trunc(self[0]), _math.trunc(self[1]), _math.trunc(self[2]))

    def __mod__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return Vec3(
                self[0] % other[0], self[1] % other[1], self[2] % other[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] % other, self[1] % other, self[2] % other  # type: ignore
            )

    def __pow__(self, other: Vec3 | tuple[float, float, float] | float) -> Vec3:
        try:
            return Vec3(
                self[0] ** other[0], self[1] ** other[1], self[2] ** other[2]  # type: ignore
            )
        except TypeError:
            return Vec3(
                self[0] ** other, self[1] ** other, self[2] ** other  # type: ignore
            )

    def __lt__(self, other: Vec3 | tuple[float, float, float]) -> bool:
        return self[0] ** 2 + self[1] ** 2 + self[2] ** 2 < other[0] ** 2 + other[1] ** 2 + other[2] ** 2

    @classmethod
    def from_pitch_yaw(cls, pitch: float, yaw: float) -> Vec3:
        """Create a unit vector from pitch and yaw in radians.

        Args:
            pitch: The pitch value in radians
            yaw: The yaw value in radians
        """
        return Vec3(
            _math.cos(yaw) * _math.cos(pitch),
            _math.sin(pitch),
            _math.sin(yaw) * _math.cos(pitch),
        ).normalize()

    def get_pitch_yaw(self) -> tuple[float, float]:
        """Get the pitch and yaw angles from a unit vector in radians."""
        return _math.asin(self.y), _math.atan2(self.z, self.x)

    def length(self) -> float:
        """Calculate the length of the vector: ``sqrt(x ** 2 + y ** 2 + z ** 2)``."""
        return _math.sqrt(self[0] ** 2 + self[1] ** 2 + self[2] ** 2)

    def length_squared(self) -> float:
        """Calculate the squared length of the vector.

        This is simply shortcut for `x ** 2 + y ** 2 + z ** 2` and can be used
        for faster comparisons without the need for a square root.
        """
        return self[0] ** 2 + self[1] ** 2 + self[2] ** 2

    def cross(self, other: Vec3 | tuple[float, float, float]) -> Vec3:
        """Calculate the cross product of this vector and another 3D vector.

        Args:
            other: Another Vec3 or tuple of 3 floats.
        """
        return Vec3(
            (self.y * other[2]) - (self.z * other[1]),
            (self.z * other[0]) - (self.x * other[2]),
            (self.x * other[1]) - (self.y * other[0]),
        )

    def dot(self, other: Vec3 | tuple[float, float, float]) -> float:
        """Calculate the dot product of this vector and another 3D vector.

        Args:
            other: Another Vec3 or tuple of 3 floats.
        """
        return self.x * other[0] + self.y * other[1] + self.z * other[2]

    def lerp(self, other: Vec3 | tuple[float, float, float], alpha: float) -> Vec3:
        """Create a new Vec3 linearly interpolated between this vector and another Vec3-like.

        Args:
          other: Another Vec3 instance or tuple of 3 floats.
          alpha: The amount of interpolation between this vector, and the other
                 vector. This should be a value between 0.0 and 1.0. For example:
                 0.5 is the midway point between both vectors.
        """
        return Vec3(
            self.x + (alpha * (other[0] - self.x)),
            self.y + (alpha * (other[1] - self.y)),
            self.z + (alpha * (other[2] - self.z)),
        )

    def distance(self, other: Vec3 | tuple[float, float, float]) -> float:
        """Calculate the distance between this vector and another 3D vector.

        Args:
            other: The point to calculate the distance to.
        """
        return _math.sqrt(((other[0] - self.x) ** 2) + ((other[1] - self.y) ** 2) + ((other[2] - self.z) ** 2))

    def normalize(self) -> Vec3:
        """Return a normalized version of the vector.

        This simply means the vector will have a length of 1.0. If the vector
        has a length of 0, the original vector will be returned.
        """
        try:
            d = _math.sqrt(self[0] ** 2 + self[1] ** 2 + self[2] ** 2)
            return Vec3(self.x / d, self.y / d, self.z / d)
        except ZeroDivisionError:
            return self

    if _typing.TYPE_CHECKING:
        @_typing.overload
        def clamp(self, min_val: float, max_val: float) -> Vec3:
            ...

        @_typing.overload
        def clamp(self, min_val: Vec3 | tuple[float, float, float], max_val: Vec3 | tuple[float, float, float]) -> Vec3:
            ...

        # -- Begin revert if perf-impacting block --
        @_typing.overload
        def clamp(self, min_val: Vec3 | tuple[float, float, float], max_val: float) -> Vec3:
            ...

        @_typing.overload
        def clamp(self, min_val: float, max_val: Vec3 | tuple[float, float, float]) -> Vec3:
            ...
        # -- End revert if perf-impacting block --

    def clamp(self, min_val: float | Vec3 | tuple[float, float, float],
              max_val: float | Vec3 | tuple[float, float, float]) -> Vec3:
        """Restrict the value of the X, Y and Z components of the vector to be within the given values.

        If a single value is provided, it will be used for all components.
        If a tuple or Vec3 is provided, the first value will be used for X, the second for Y, and the third for Z.

        Args:
            min_val: The minimum value(s)
            max_val: The maximum value(s)
        """
        try:
            min_x, min_y, min_z = min_val[0], min_val[1], min_val[2]  # type: ignore
        except TypeError:
            min_x = min_val
            min_y = min_val
            min_z = min_val
        try:
            max_x, max_y, max_z = max_val[0], max_val[1], max_val[2]  # type: ignore
        except TypeError:
            max_x = max_val
            max_y = max_val
            max_z = max_val

        return Vec3(
            clamp(self[0], min_x, max_x), clamp(self[1], min_y, max_y), clamp(self[2], min_z, max_z)  # type: ignore
        )

    def index(self, *args: _typing.Any) -> int:
        raise NotImplementedError("Vec types can be indexed directly.")

    def __getattr__(self, attrs: str) -> Vec2 | Vec3 | Vec4:
        try:
            # Allow swizzled getting of attrs
            vec_class = {2: Vec2, 3: Vec3, 4: Vec4}[len(attrs)]
            return vec_class(*(self['xyz'.index(c)] for c in attrs))
        except (ValueError, KeyError, TypeError) as err:
            msg = f"'Vec3' has no attribute: '{attrs}'."
            raise AttributeError(msg) from err


class Vec4(_typing.NamedTuple):
    """A four-dimensional vector represented as X Y Z W coordinates.

    `Vec4` is an immutable 4D Vector, including most common operators.
    As an immutable type, all operations return a new object.

    .. note:: The Python ``len` operator returns the number of elements in
              the vector. For the vector length, use the `length()` method.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0

    def __bool__(self):
        return self.x != 0.0 or self.y != 0.0 or self.z != 0.0 or self.w != 0.0

    def __add__(self, other: Vec4 | tuple[float, float, float, float] | float) -> Vec4:
        try:
            return Vec4(
                other[0] + self[0], other[1] + self[1], other[2] + self[2], other[3] + self[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                other + self[0], other + self[1], other + self[2], other + self[3]  # type: ignore
            )

    def __radd__(self, other: Vec4 | tuple[float, float, float, float] | int) -> Vec4:
        try:
            return self.__add__(_typing.cast(Vec4, other))
        except TypeError as err:
            if other == 0:  # Required for functionality with sum()
                return self
            raise err

    def __sub__(self, other: Vec4 | tuple[float, float, float, float] | float) -> Vec4:
        try:
            return Vec4(
                self[0] - other[0], self[1] - other[1], self[2] - other[2], self[3] - other[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] - other, self[1] - other, self[2] - other, self[3] - other  # type: ignore
            )

    def __rsub__(self, other: Vec4 | tuple[float, float, float, float] | float) -> Vec4:
        try:
            return Vec4(
                other[0] - self[0], other[1] - self[1], other[2] - self[2], other[3] - self[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                other - self[0], other - self[1], other - self[2], other - self[3]  # type: ignore
            )

    def __mul__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                self[0] * scalar[0], self[1] * scalar[1], self[2] * scalar[2], self[3] * scalar[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] * scalar, self[1] * scalar, self[2] * scalar, self[3] * scalar  # type: ignore
            )

    def __rmul__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                self[0] * scalar[0], self[1] * scalar[1], self[2] * scalar[2], self[3] * scalar[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] * scalar, self[1] * scalar, self[2] * scalar, self[3] * scalar  # type: ignore
            )

    def __truediv__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                self[0] / scalar[0], self[1] / scalar[1], self[2] / scalar[2], self[3] / scalar[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] / scalar, self[1] / scalar, self[2] / scalar, self[3] / scalar  # type: ignore
            )

    def __rtruediv__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                scalar[0] / self[0], scalar[1] / self[1], scalar[2] / self[2], scalar[3] / self[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                scalar / self[0], scalar / self[1], scalar / self[2], scalar / self[3]  # type: ignore
            )

    def __floordiv__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                self[0] // scalar[0], self[1] // scalar[1], self[2] // scalar[2], self[3] // scalar[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] // scalar, self[1] // scalar, self[2] // scalar, self[3] // scalar  # type: ignore
            )

    def __rfloordiv__(self, scalar: float | Vec4 | tuple[float, float, float, float]) -> Vec4:
        try:
            return Vec4(
                scalar[0] // self[0], scalar[1] // self[1], scalar[2] // self[2], scalar[3] // self[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                scalar // self[0], scalar // self[1], scalar // self[2], scalar // self[3]  # type: ignore
            )

    def __abs__(self) -> Vec4:
        return Vec4(abs(self[0]), abs(self[1]), abs(self[2]), abs(self[3]))

    def __neg__(self) -> Vec4:
        return Vec4(-self.x, -self.y, -self.z, -self.w)

    def __round__(self, n_digits: int | None = None) -> Vec4:
        return Vec4(*(round(v, n_digits) for v in self))

    def __ceil__(self) -> Vec4:
        return Vec4(_math.ceil(self[0]), _math.ceil(self[1]), _math.ceil(self[2]), _math.ceil(self[3]))

    def __floor__(self) -> Vec4:
        return Vec4(_math.floor(self[0]), _math.floor(self[1]), _math.floor(self[2]), _math.floor(self[3]))

    def __trunc__(self) -> Vec4:
        return Vec4(_math.trunc(self[0]), _math.trunc(self[1]), _math.trunc(self[2]), _math.trunc(self[3]))

    def __mod__(self, other: Vec4 | tuple[int, int, int, int] | float) -> Vec4:
        try:
            return Vec4(
                self[0] % other[0], self[1] % other[1], self[2] % other[2], self[3] % other[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] % other, self[1] % other, self[2] % other, self[3] % other  # type: ignore
            )

    def __pow__(self, other: Vec4 | tuple[int, int, int, int] | float) -> Vec4:
        try:
            return Vec4(
                self[0] ** other[0], self[1] ** other[1], self[2] ** other[2], self[3] ** other[3]  # type: ignore
            )
        except TypeError:
            return Vec4(
                self[0] ** other, self[1] ** other, self[2] ** other, self[3] ** other  # type: ignore
            )

    def __lt__(self, other: Vec4 | tuple[float, float, float, float]) -> bool:
        return (self[0] ** 2 + self[1] ** 2 + self[2] ** 2 + self[3] ** 2 <
                other[0] ** 2 + other[1] ** 2 + other[2] ** 2 + other[3] ** 2)

    def length(self) -> float:
        """Calculate the length of the vector: ``sqrt(x ** 2 + y ** 2 + z ** 2 + w ** 2)``."""
        return _math.sqrt(self[0] ** 2 + self[1] ** 2 + self[2] ** 2 + self[3] ** 2)

    def length_squared(self) -> float:
        """Calculate the squared length of the vector.

        This is simply shortcut for `x ** 2 + y ** 2 + z ** 2 + w ** 2` and can be used
        for faster comparisons without the need for a square root.
        """
        return self[0] ** 2 + self[1] ** 2 + self[2] ** 2 + self[3] ** 2

    def lerp(self, other: Vec4 | tuple[float, float, float, float], amount: float) -> Vec4:
        """Create a new Vec4 linearly interpolated between this vector and another Vec4.

        Args:
          other: Another Vec4 instance.
          amount: The amount of interpolation between this vector, and the other
                  vector. This should be a value between 0.0 and 1.0. For example:
                  0.5 is the midway point between both vectors.
        """
        return Vec4(
            self.x + (amount * (other.x - self.x)),
            self.y + (amount * (other.y - self.y)),
            self.z + (amount * (other.z - self.z)),
            self.w + (amount * (other.w - self.w)),
        )

    def distance(self, other: Vec4 | tuple[float, float, float, float]) -> float:
        """Calculate the distance between this vector and another 4D vector.

        Args:
            other: The point to calculate the distance to.
        """
        return _math.sqrt(
            ((other.x - self.x) ** 2)
            + ((other.y - self.y) ** 2)
            + ((other.z - self.z) ** 2)
            + ((other.w - self.w) ** 2),
        )

    def normalize(self) -> Vec4:
        """Returns a normalized version of the vector meaning a version that has length 1.

        This means that the vector will have the same direction, but a length of 1.0.
        If the vector has a length of 0, the original vector will be returned.
        """
        if d := _math.sqrt(self[0] ** 2 + self[1] ** 2 + self[2] ** 2 + self[3] ** 2):
            return Vec4(self[0] / d, self[1] / d, self[2] / d, self[3] / d)
        return self

    if _typing.TYPE_CHECKING:
        @_typing.overload
        def clamp(self, min_val: float, max_val: float) -> Vec4:
            ...

        @_typing.overload
        def clamp(self, min_val: tuple[float, float, float, float], max_val: tuple[float, float, float, float]) -> Vec4:
            ...

        # -- Begin revert if perf-impacting block --
        @_typing.overload
        def clamp(self, min_val: tuple[float, float, float, float], max_val: float) -> Vec4:
            ...

        @_typing.overload
        def clamp(self, min_val: float, max_val: tuple[float, float, float, float]) -> Vec4:
            ...
        # -- End revert if perf-impacting block --

    def clamp(
        self,
        min_val: float | tuple[float, float, float, float],
        max_val: float | tuple[float, float, float, float],
    ) -> Vec4:
        """Restrict the value of the X, Y, Z and W components of the vector to be within the given values.

        The minimum and maximum values can be a single value that will be applied to all components,
        or a tuple of 4 values that will be applied to each component respectively.

        Args:
            min_val: The minimum value(s)
            max_val: The maximum value(s)
        """
        try:
            min_x, min_y, min_z, min_w = min_val[0], min_val[1], min_val[2], min_val[3]  # type: ignore
        except TypeError:
            min_x = min_val
            min_y = min_val
            min_z = min_val
            min_w = min_val
        try:
            max_x, max_y, max_z, max_w = max_val[0], max_val[1],  max_val[2], max_val[3]  # type: ignore
        except TypeError:
            max_x = max_val
            max_y = max_val
            max_z = max_val
            max_w = max_val

        return Vec4(
            clamp(self[0], min_x, max_x), clamp(self[1], min_y, max_y),  # type: ignore
            clamp(self[2], min_z, max_z), clamp(self[3], min_w, max_w),  # type: ignore
        )

    def dot(self, other: Vec4 | tuple[float, float, float, float]) -> float:
        """Calculate the dot product of this vector and another 4D vector.

        Args:
            other: Another Vec4 instance.
        """
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def index(self, *args: _typing.Any) -> int:
        raise NotImplementedError("Vec types can be indexed directly.")

    def __getattr__(self, attrs: str) -> Vec2 | Vec3 | Vec4:
        try:
            # Allow swizzled getting of attrs
            vec_class = {2: Vec2, 3: Vec3, 4: Vec4}[len(attrs)]
            return vec_class(*(self['xyzw'.index(c)] for c in attrs))
        except (ValueError, KeyError, TypeError) as err:
            msg = f"'Vec4' has no attribute: '{attrs}'."
            raise AttributeError(msg) from err