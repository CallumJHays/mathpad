import sympy

from mathpad.core.dimensions import Angle
from mathpad.core.val import Q, Dimensionless


def sin(x: Q[Angle]) -> Dimensionless:
    return Dimensionless(1, sympy.sin(x.expr))  # type: ignore


def cos(x: Q[Angle]) -> Dimensionless:
    return Dimensionless(1, sympy.cos(x.expr))  # type: ignore


def tan(x: Q[Angle]) -> Dimensionless:
    return Dimensionless(1, sympy.tan(x.expr))  # type: ignore
