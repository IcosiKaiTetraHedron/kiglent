"""Matrix math.

This module provides Matrix objects, including Mat3 and Mat4.
Most common matrix operations are supported.
Helper methods are included for rotating, scaling, and transforming.
The :py:class:`~pyglet.matrix.Mat4` includes class methods
for creating orthographic and perspective projection matrixes.

Matrices behave just like they do in GLSL: they are specified in column-major
order and multiply on the left of vectors, which are treated as columns.

All objects are immutable and hashable.
"""

from __future__ import annotations

import math as _math
import typing as _typing
import warnings as _warnings

if _typing.TYPE_CHECKING:
    from kiglent.vector import Vec3, Vec4


class Mat3(_typing.NamedTuple):
    """A 3x3 Matrix.

    `Mat3` is an immutable 3x3 Matrix, which includes most common operators.

    A Matrix can be created with a list or tuple of 9 values.
    If no values are provided, an "identity matrix" will be created
    (1.0 on the main diagonal). Because Mat3 objects are immutable,
    all operations return a new Mat3 object.

    .. note:: Matrix multiplication is performed using the "@" operator.
    """

    a: float = 1.0
    b: float = 0.0
    c: float = 0.0

    d: float = 0.0
    e: float = 1.0
    f: float = 0.0

    g: float = 0.0
    h: float = 0.0
    i: float = 1.0

    def scale(self, sx: float, sy: float) -> Mat3:
        return self @ Mat3(1.0 / sx, 0.0, 0.0, 0.0, 1.0 / sy, 0.0, 0.0, 0.0, 1.0)

    def translate(self, tx: float, ty: float) -> Mat3:
        return self @ Mat3(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -tx, ty, 1.0)

    def rotate(self, phi: float) -> Mat3:
        s = _math.sin(_math.radians(phi))
        c = _math.cos(_math.radians(phi))
        return self @ Mat3(c, s, 0.0, -s, c, 0.0, 0.0, 0.0, 1.0)

    def shear(self, sx: float, sy: float) -> Mat3:
        return self @ Mat3(1.0, sy, 0.0, sx, 1.0, 0.0, 0.0, 0.0, 1.0)

    def __add__(self, other: Mat3) -> Mat3:
        if not isinstance(other, Mat3):
            raise TypeError("Can only add to other Mat3 types")
        return Mat3(*(s + o for s, o in zip(self, other)))

    def __sub__(self, other: Mat3) -> Mat3:
        if not isinstance(other, Mat3):
            raise TypeError("Can only subtract from other Mat3 types")
        return Mat3(*(s - o for s, o in zip(self, other)))

    def __pos__(self) -> Mat3:
        return self

    def __neg__(self) -> Mat3:
        return Mat3(*(-v for v in self))

    def __invert__(self) -> Mat3:
        # extract the elements in row-column form. (matrix is stored column first)
        a11, a12, a13, a21, a22, a23, a31, a32, a33 = self

        # Calculate Adj(self) values column-row order
        # | a d g |
        # | b e h |
        # | c f i |
        a = a22 * a33 - a32 * a23  # +
        b = a31 * a23 - a21 * a33  # -
        c = a21 * a32 - a22 * a31  # +
        d = a32 * a13 - a12 * a33  # -
        e = a11 * a33 - a31 * a13  # +
        f = a31 * a12 - a11 * a32  # -
        g = a12 * a23 - a22 * a13  # +
        h = a21 * a13 - a11 * a23  # -
        i = a11 * a22 - a21 * a12  # +

        # Calculate determinant
        det = a11 * a + a21 * d + a31 * g

        if det == 0:
            _warnings.warn("Unable to calculate inverse of singular Matrix")
            return self

        # get determinant reciprocal
        rep = 1.0 / det

        # get inverse: A^-1 = def(A)^-1 * adj(A)
        return Mat3(*(a * rep, b * rep, c * rep,
                      d * rep, e * rep, f * rep,
                      g * rep, h * rep, i * rep))

    def __round__(self, ndigits: int | None = None) -> Mat3:
        return Mat3(*(round(v, ndigits) for v in self))

    def __mul__(self, other: object) -> _typing.NoReturn:
        msg = "Please use the @ operator for Matrix multiplication."
        raise NotImplementedError(msg)

    @_typing.overload
    def __matmul__(self, other: Vec3) -> Vec3: ...

    @_typing.overload
    def __matmul__(self, other: Mat3) -> Mat3: ...

    def __matmul__(self, other) -> Vec3 | Mat3:
        try:
            # extract the elements in row-column form. (matrix is stored column first)
            a11, a12, a13, a21, a22, a23, a31, a32, a33 = self
            b11, b12, b13, b21, b22, b23, b31, b32, b33 = other

            # Multiply and sum rows * columns
            return Mat3(
                # Column 1
                a11 * b11 + a21 * b12 + a31 * b13, a12 * b11 + a22 * b12 + a32 * b13, a13 * b11 + a23 * b12 + a33 * b13,
                # Column 2
                a11 * b21 + a21 * b22 + a31 * b23, a12 * b21 + a22 * b22 + a32 * b23, a13 * b21 + a23 * b22 + a33 * b23,
                # Column 3
                a11 * b31 + a21 * b32 + a31 * b33, a12 * b31 + a22 * b32 + a32 * b33, a13 * b31 + a23 * b32 + a33 * b33,
            )
        except ValueError:
            x, y, z = other
            # extract the elements in row-column form. (matrix is stored column first)
            a11, a12, a13, a21, a22, a23, a31, a32, a33 = self
            return Vec3(
                a11 * x + a21 * y + a31 * z,
                a12 * x + a22 * y + a32 * z,
                a13 * x + a23 * y + a33 * z,
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self[0:3]}\n    {self[3:6]}\n    {self[6:9]}"


class Mat4(_typing.NamedTuple):
    """A 4x4 Matrix.

    ``Mat4`` is an immutable 4x4 Matrix object with most common operators.
    This includes class methods for creating orthogonal and perspective
    projection matrixes, which can be used directly by OpenGL.

    You can create a Matrix with 16 initial values (floats), or no values
    at all. If no values are provided, an "identity matrix" will be created
    (1.0 on the main diagonal). ``Mat4`` objects are immutable, so all
    operations will return a new Mat4 object.

    Note:
        Matrix multiplication is performed using the "@" operator.
    """

    a: float = 1.0
    b: float = 0.0
    c: float = 0.0
    d: float = 0.0

    e: float = 0.0
    f: float = 1.0
    g: float = 0.0
    h: float = 0.0

    i: float = 0.0
    j: float = 0.0
    k: float = 1.0
    l: float = 0.0

    m: float = 0.0
    n: float = 0.0
    o: float = 0.0
    p: float = 1.0

    @classmethod
    def orthogonal_projection(cls: type[Mat4], left: float, right: float, bottom: float, top: float,
                              z_near: float, z_far: float) -> Mat4:
        """Create a Mat4 orthographic projection matrix for use with OpenGL.

        Given left, right, bottom, top values, and near/far z planes,
        create a 4x4 Projection Matrix. This is useful for setting
        :py:attr:`~pyglet.window.Window.projection`.
        """
        width = right - left
        height = top - bottom
        depth = z_far - z_near

        s_x = 2.0 / width
        s_y = 2.0 / height
        s_z = 2.0 / -depth

        t_x = -(right + left) / width
        t_y = -(top + bottom) / height
        t_z = -(z_far + z_near) / depth

        return cls(s_x, 0.0, 0.0, 0.0,
                   0.0, s_y, 0.0, 0.0,
                   0.0, 0.0, s_z, 0.0,
                   t_x, t_y, t_z, 1.0)

    @classmethod
    def perspective_projection(cls: type[Mat4], aspect: float, z_near: float, z_far: float, fov: float = 60) -> Mat4:
        """Create a Mat4 perspective projection matrix for use with OpenGL.

        Given a desired aspect ratio, near/far planes, and fov (field of view),
        create a 4x4 Projection Matrix. This is useful for setting
        :py:attr:`~pyglet.window.Window.projection`.
        """
        xy_max = z_near * _math.tan(fov * _math.pi / 360)
        y_min = -xy_max
        x_min = -xy_max

        width = xy_max - x_min
        height = xy_max - y_min
        depth = z_far - z_near
        q = -(z_far + z_near) / depth
        qn = -2 * z_far * z_near / depth

        w = 2 * z_near / width
        w = w / aspect
        h = 2 * z_near / height

        return cls(w, 0, 0, 0,
                   0, h, 0, 0,
                   0, 0, q, -1,
                   0, 0, qn, 0)

    @classmethod
    def from_rotation(cls, angle: float, vector: Vec3) -> Mat4:
        """Create a rotation matrix from an angle and Vec3.

        Args:
          angle: The desired angle, in radians.
          vector: A Vec3 indicating the direction.
        """
        return cls().rotate(angle, vector)

    @classmethod
    def from_scale(cls: type[Mat4], vector: Vec3) -> Mat4:
        """Create a scale matrix from a Vec3."""
        return cls(vector.x, 0.0, 0.0, 0.0,
                   0.0, vector.y, 0.0, 0.0,
                   0.0, 0.0, vector.z, 0.0,
                   0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_translation(cls: type[Mat4], vector: Vec3) -> Mat4:
        """Create a translation matrix from a Vec3."""
        return cls(1.0, 0.0, 0.0, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   0.0, 0.0, 1.0, 0.0,
                   vector.x, vector.y, vector.z, 1.0)

    @classmethod
    def look_at(cls: type[Mat4], position: Vec3, target: Vec3, up: Vec3) -> Mat4:
        """Create a viewing matrix that points toward a target.

        This method takes three Vec3s, describing the viewer's position,
        where they are looking, and the upward axis (typically positive
        on the Y axis). The resulting Mat4 can be used as the projection
        matrix.

        Args:
          position: The location of the viewer in the scene.
          target: The point that the viewer is looking towards.
          up: A vector pointing "up" in the scene, typically `Vec3(0.0, 1.0, 0.0)`.
        """
        f = (target - position).normalize()
        u = up.normalize()
        s = f.cross(u).normalize()
        u = s.cross(f)

        return cls(s.x, u.x, -f.x, 0.0,
                   s.y, u.y, -f.y, 0.0,
                   s.z, u.z, -f.z, 0.0,
                   -s.dot(position), -u.dot(position), f.dot(position), 1.0)

    def row(self, index: int) -> tuple:
        """Get a specific row as a tuple."""
        return self[index::4]

    def column(self, index: int) -> tuple:
        """Get a specific column as a tuple."""
        return self[index * 4: index * 4 + 4]

    def rotate(self, angle: float, vector: Vec3) -> Mat4:
        a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
        
        x, y, z = vector
        d = _math.sqrt(x ** 2 + y ** 2 + z ** 2)
        if d != 0.0:
            x = x / d
            y = y / d
            z = z / d
        c = _math.cos(angle)
        s = _math.sin(angle)
        t = 1 - c
        t_x, t_y, t_z = t * x, t * y, t * z

        b11 = c + t_x * x
        b12 = t_x * y + s * z
        b13 = t_x * z - s * y
        b21 = t_y * x - s * z
        b22 = c + t_y * y
        b23 = t_y * z + s * x
        b31 = t_z * x + s * y
        b32 = t_z * y - s * x
        b33 = c + t_z * z
        
        return Mat4(
            # Column 1
            a11 * b11 + a21 * b12 + a31 * b13, a12 * b11 + a22 * b12 + a32 * b13,
            a13 * b11 + a23 * b12 + a33 * b13, a14 * b11 + a24 * b12 + a34 * b13,
            # Column 2
            a11 * b21 + a21 * b22 + a31 * b23, a12 * b21 + a22 * b22 + a32 * b23,
            a13 * b21 + a23 * b22 + a33 * b23, a14 * b21 + a24 * b22 + a34 * b23,
            # Column 3
            a11 * b31 + a21 * b32 + a31 * b33, a12 * b31 + a22 * b32 + a32 * b33,
            a13 * b31 + a23 * b32 + a33 * b33, a14 * b31 + a24 * b32 + a34 * b33,
            # Column 4
            a41, a42, a43, a44,
        )

    def rotate_z(self, angle: float) -> Mat4:
        a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
        
        c = _math.cos(angle)
        s = _math.sin(angle)

        return Mat4(
            a11 * c + a21 * s, a12 * c + a22 * s,
            a13 * c + a23 * s, a14 * c + a24 * s,
            -a11 * s + a21 * c, -a12 * s + a22 * c,
            -a13 * s + a23 * c, -a14 * s + a24 * c,
            a31, a32, a33, a34,
            a41, a42, a43, a44,
        )

    def scale(self, vector: Vec3) -> Mat4:
        """Get a scale Matrix on x, y, or z axis."""
        a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
        x, y, z = vector
        return Mat4(
            a11 * x, a12, a13, a14,
            a21, a22 * y, a23, a24,
            a31, a32, a33 * z, a34,
            a41, a42, a43, a44,
        )

    def translate(self, vector: Vec3) -> Mat4:
        """Get a translation Matrix along x, y, and z axis."""
        a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
        x, y, z = vector
        return Mat4(
            a11, a12, a13, a14,
            a21, a22, a23, a24,
            a31, a32, a33, a34,
            a11 * x + a21 * y + a31 * z + a41, a12 * x + a22 * y + a32 * z + a42,
            a13 * x + a23 * y + a33 * z + a43, a14 * x + a24 * y + a34 * z + a44,
        )

    def transpose(self) -> Mat4:
        """Get a transpose of this Matrix."""
        return Mat4(*self[0::4], *self[1::4], *self[2::4], *self[3::4])

    def __add__(self, other: Mat4) -> Mat4:
        if not isinstance(other, Mat4):
            raise TypeError("Can only add to other Mat4 types")
        return Mat4(*(s + o for s, o in zip(self, other)))

    def __sub__(self, other: Mat4) -> Mat4:
        if not isinstance(other, Mat4):
            raise TypeError("Can only subtract from other Mat4 types")
        return Mat4(*(s - o for s, o in zip(self, other)))

    def __pos__(self) -> Mat4:
        return self

    def __neg__(self) -> Mat4:
        return Mat4(*(-v for v in self))

    def __invert__(self) -> Mat4:
        # extract the elements in row-column form. (matrix is stored column first)
        a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self

        a = a33 * a44 - a34 * a43
        b = a32 * a44 - a34 * a42
        c = a32 * a43 - a33 * a42
        d = a31 * a44 - a34 * a41
        e = a31 * a43 - a33 * a41
        f = a31 * a42 - a32 * a41
        g = a23 * a44 - a24 * a43
        h = a22 * a44 - a24 * a42
        i = a22 * a43 - a23 * a42
        j = a23 * a34 - a24 * a33
        k = a22 * a34 - a24 * a32
        l = a22 * a33 - a23 * a32
        m = a21 * a44 - a24 * a41
        n = a21 * a43 - a23 * a41
        o = a21 * a34 - a24 * a31
        p = a21 * a33 - a23 * a31
        q = a21 * a42 - a22 * a41
        r = a21 * a32 - a22 * a31

        det = (a11 * (a22 * a - a23 * b + a24 * c) -
               a12 * (a21 * a - a23 * d + a24 * e) +
               a13 * (a21 * b - a22 * d + a24 * f) -
               a14 * (a21 * c - a22 * e + a23 * f))

        if det == 0:
            _warnings.warn("Unable to calculate inverse of singular Matrix")
            return self

        pdet = 1 / det
        ndet = -pdet

        return Mat4(pdet * (a22 * a - a23 * b + a24 * c),
                    ndet * (a12 * a - a13 * b + a14 * c),
                    pdet * (a12 * g - a13 * h + a14 * i),
                    ndet * (a12 * j - a13 * k + a14 * l),
                    ndet * (a21 * a - a23 * d + a24 * e),
                    pdet * (a11 * a - a13 * d + a14 * e),
                    ndet * (a11 * g - a13 * m + a14 * n),
                    pdet * (a11 * j - a13 * o + a14 * p),
                    pdet * (a21 * b - a22 * d + a24 * f),
                    ndet * (a11 * b - a12 * d + a14 * f),
                    pdet * (a11 * h - a12 * m + a14 * q),
                    ndet * (a11 * k - a12 * o + a14 * r),
                    ndet * (a21 * c - a22 * e + a23 * f),
                    pdet * (a11 * c - a12 * e + a13 * f),
                    ndet * (a11 * i - a12 * n + a13 * q),
                    pdet * (a11 * l - a12 * p + a13 * r))

    def __round__(self, ndigits: int | None) -> Mat4:
        return Mat4(*(round(v, ndigits) for v in self))

    def __mul__(self, other: int) -> _typing.NoReturn:
        msg = "Please use the @ operator for Matrix multiplication."
        raise NotImplementedError(msg)

    @_typing.overload
    def __matmul__(self, other: Vec4) -> Vec4: ...

    @_typing.overload
    def __matmul__(self, other: Mat4) -> Mat4: ...

    def __matmul__(self, other):
        try:
            # extract the elements in row-column form. (matrix is stored column first)
            a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
            b11, b12, b13, b14, b21, b22, b23, b24, b31, b32, b33, b34, b41, b42, b43, b44 = other
            # Multiply and sum rows * columns:
            return Mat4(
                # Column 1
                a11 * b11 + a21 * b12 + a31 * b13 + a41 * b14, a12 * b11 + a22 * b12 + a32 * b13 + a42 * b14,
                a13 * b11 + a23 * b12 + a33 * b13 + a43 * b14, a14 * b11 + a24 * b12 + a34 * b13 + a44 * b14,
                # Column 2
                a11 * b21 + a21 * b22 + a31 * b23 + a41 * b24, a12 * b21 + a22 * b22 + a32 * b23 + a42 * b24,
                a13 * b21 + a23 * b22 + a33 * b23 + a43 * b24, a14 * b21 + a24 * b22 + a34 * b23 + a44 * b24,
                # Column 3
                a11 * b31 + a21 * b32 + a31 * b33 + a41 * b34, a12 * b31 + a22 * b32 + a32 * b33 + a42 * b34,
                a13 * b31 + a23 * b32 + a33 * b33 + a43 * b34, a14 * b31 + a24 * b32 + a34 * b33 + a44 * b34,
                # Column 4
                a11 * b41 + a21 * b42 + a31 * b43 + a41 * b44, a12 * b41 + a22 * b42 + a32 * b43 + a42 * b44,
                a13 * b41 + a23 * b42 + a33 * b43 + a43 * b44, a14 * b41 + a24 * b42 + a34 * b43 + a44 * b44,
            )
        except ValueError:
            x, y, z, w = other
            # extract the elements in row-column form. (matrix is stored column first)
            a11, a12, a13, a14, a21, a22, a23, a24, a31, a32, a33, a34, a41, a42, a43, a44 = self
            return Vec4(
                x * a11 + y * a21 + z * a31 + w * a41,
                x * a12 + y * a22 + z * a32 + w * a42,
                x * a13 + y * a23 + z * a33 + w * a43,
                x * a14 + y * a24 + z * a34 + w * a44,
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self[0:4]}\n    {self[4:8]}\n    {self[8:12]}\n    {self[12:16]}"


class Quaternion(_typing.NamedTuple):
    """Quaternion.

    Quaternions are 4-dimensional complex numbers, useful for describing 3D rotations.
    """

    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @classmethod
    def from_mat3(cls) -> Quaternion:
        raise NotImplementedError

    @classmethod
    def from_mat4(cls) -> Quaternion:
        raise NotImplementedError

    def to_mat4(self) -> Mat4:
        """Calculate a 4x4 transform matrix which applies a rotation."""

        w = self.w
        x = self.x
        y = self.y
        z = self.z

        a = 1 - (y**2 + z**2) * 2
        b = 2 * (x * y - z * w)
        c = 2 * (x * z + y * w)

        e = 2 * (x * y + z * w)
        f = 1 - (x**2 + z**2) * 2
        g = 2 * (y * z - x * w)

        i = 2 * (x * z - y * w)
        j = 2 * (y * z + x * w)
        k = 1 - (x**2 + y**2) * 2

        # a, b, c, -
        # e, f, g, -
        # i, j, k, -
        # -, -, -, -

        return Mat4(a, b, c, 0.0, e, f, g, 0.0, i, j, k, 0.0, 0.0, 0.0, 0.0, 1.0)

    def to_mat3(self) -> Mat3:
        """Create a 3x3 rotation matrix."""

        w = self.w
        x = self.x
        y = self.y
        z = self.z

        a = 1 - (y**2 + z**2) * 2
        b = 2 * (x * y - z * w)
        c = 2 * (x * z + y * w)

        e = 2 * (x * y + z * w)
        f = 1 - (x**2 + z**2) * 2
        g = 2 * (y * z - x * w)

        i = 2 * (x * z - y * w)
        j = 2 * (y * z + x * w)
        k = 1 - (x**2 + y**2) * 2

        # a, b, c, -
        # e, f, g, -
        # i, j, k, -
        # -, -, -, -

        return Mat3(*(a, b, c, e, f, g, i, j, k))

    def length(self) -> float:
        """Calculate the length of the quaternion from the origin."""
        return _math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def conjugate(self) -> Quaternion:
        """Calculate the conjugate of this quaternion.

        This operation:
        #. leaves the :py:attr:`.w` component alone
        #. inverts the sign of the :py:attr:`.x`, :py:attr:`.y`, and :py:attr:`.z` components

        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def dot(self, other: Quaternion) -> float:
        """Calculate the dot product with another quaternion."""
        a, b, c, d = self
        e, f, g, h = other
        return a * e + b * f + c * g + d * h

    def normalize(self) -> Quaternion:
        """Calculate a unit quaternion from the instance.

        The returned quaternion will be a scaled-down version
        of the instance which has:

        * a length of ``1``
        * the same relative of its components
        """
        m = self.length()
        if m == 0:
            return self
        return Quaternion(self.w / m, self.x / m, self.y / m, self.z / m)

    def __add__(self, other: Quaternion) -> Quaternion:
        a, b, c, d = self
        e, f, g, h = other
        return Quaternion(a + e, b + f, c + g, d + h)

    def __sub__(self, other: Quaternion) -> Quaternion:
        a, b, c, d = self
        e, f, g, h = other
        return Quaternion(a - e, b - f, c - g, d - h)

    def __mul__(self, scalar: float) -> Quaternion:
        w, x = self.w * scalar, self.x * scalar
        y, z = self.y * scalar, self.z * scalar
        return Quaternion(w, x, y, z)

    def __truediv__(self, other: Quaternion) -> Quaternion:
        return ~self @ other

    def __invert__(self) -> Quaternion:
        return self.conjugate() * (1 / self.dot(self))

    def __matmul__(self, other: Quaternion) -> Quaternion:
        a, u = self.w, Vec3(*self[1:])
        b, v = other.w, Vec3(*other[1:])
        scalar = a * b - u.dot(v)
        vector = v * a + u * b + u.cross(v)
        return Quaternion(scalar, *vector)

