import sympy
from mathpad import *


def sin(x: Q[Angle]):
    return Dimensionless(1, sympy.sin(x.val))  # type: ignore


def cos(x: Q[Angle]):
    return Dimensionless(1, sympy.cos(x.val))  # type: ignore


def tan(x: Q[Angle]):
    return Dimensionless(1, sympy.tan(x.val))  # type: ignore


# TODO: add more trig functions


def sine_rule(
    a: Q[Length],  # length of side a
    b: Q[Length],  # length of side b
    alpha: Q[Angle],  # internal angle opposite to side a
    beta: Q[Angle],  # internal angle opposite to side b
) -> Equation:
    "Relates lengths of two sides of any triangle the internal angle opposite"
    return a == b * sin(alpha) / sin(beta)


def cosine_rule(
    a: Q[Length],  # length of side a
    b: Q[Length],  # length of side b
    c: Q[Length],  # length of side c
    C: Q[Angle],  # internal angle opposite to side c
) -> Equation:
    return c ** 2 == a ** 2 + b ** 2 - 2 * a * b * cos(C)
