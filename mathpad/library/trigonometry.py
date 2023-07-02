
from mathpad.core import *
from .mathpad_constructor import mathpad_constructor


def sine_rule(
    a: Q[Length],  # length of side a
    b: Q[Length],  # length of side b
    alpha: Q[Angle],  # internal angle opposite to side a
    beta: Q[Angle],  # internal angle opposite to side b
) -> Equation[Length]:
    "Relates lengths of two sides of any triangle the internal angle opposite"
    return a == b * sin(alpha) / sin(beta) # type: ignore


def cosine_rule(
    a: Q[Length],  # length of side a
    b: Q[Length],  # length of side b
    c: Q[Length],  # length of side c
    C: Q[Angle],  # internal angle opposite to side c
) -> Equation[Area]:
    return c ** 2 == a ** 2 + b ** 2 - 2 * a * b * cos(C) # type: ignore
