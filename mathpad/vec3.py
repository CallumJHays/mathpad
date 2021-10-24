from typing import Generic, Sequence
from sympy.physics.vector import vlatex

from mathpad.val import GenericVal, Q, Val
from mathpad.units import meters
from mathpad._quality_of_life import t
from mathpad.trigonometry import magnitude
from mathpad.calculus import diff

# TODO: use sympy.physics.vector.ReferenceFrame


class Vec3(Generic[GenericVal], Sequence):
    def __init__(
        self, *, i: Q[GenericVal] = 0, j: Q[GenericVal] = 0, k: Q[GenericVal] = 0
    ):
        "assumes meters if Num passed"
        set_units = None
        for attempt in [i, j, k]:
            try:
                attempt.units
                if set_units:
                    # do dimensionality check
                    # TODO: make error message better
                    i.in_units(attempt)
                set_units = attempt

            except AttributeError:
                pass

        assert set_units, "At least one input must be a Val with dimensionality"

        self.i: GenericVal = i if isinstance(i, Val) else set_units.new(i)  # type: ignore
        self.j: GenericVal = j if isinstance(j, Val) else set_units.new(j)  # type: ignore
        self.k: GenericVal = k if isinstance(k, Val) else set_units.new(k)  # type: ignore
        self._tuple = (self.i, self.j, self.k)

    def __getitem__(self, idx):
        return self._tuple[idx]

    def __iter__(self):
        return iter(self._tuple)

    def __len__(self):
        return 3

    def dot(self, other: "Vec3"):
        ai, aj, ak = self
        bi, bj, bk = other
        return ai * bi + aj * bj + ak * bk  # type: ignore

    def _repr_latex_(self):
        # use vlatex because it applies dot notation where possible

        res = (
            "\\begin{bmatrix} "
            + " \\\\ ".join(
                f'{vlatex(x.val).replace("- 1.0 ", "-")} & {"dimensionless" if x.units == 1 else vlatex(x.units)}'
                + "\\cdot \\hat{"
                + unit_vector
                + "}"
                for unit_vector, x in zip("ijk", self)
            )
            + " \\end{bmatrix}"
        )

        return f"$$ {res} $$"

    def diff(self, n: int = 1, wrt: Val = t):
        i, j, k = diff(self, n=n, wrt=wrt)  # type: ignore
        return Vec3(i=i, j=j, k=k)

    def __add__(self: "Vec3[Val]", other: "Vec3[Val]"):
        ai, aj, ak = self
        bi, bj, bk = other
        return Vec3(
            i=ai + bi,  # type: ignore
            j=aj + bj,  # type: ignore
            k=ak + bk,  # type: ignore
        )

    def __mul__(self: "Vec3[GenericVal]", other: Val):
        ai, aj, ak = self
        return Vec3(
            i=ai * other,  # type: ignore
            j=aj * other,  # type: ignore
            k=ak * other,  # type: ignore
        )

    def __rmul__(self: "Vec3[GenericVal]", other: Val):
        return self * other  # call __mull__

    def __abs__(self):
        return magnitude(*self)

    def __neg__(self):
        return Vec3(
            i=-self.i,
            j=-self.j,
            k=-self.k,
        )