import sympy

from mathpad.units import seconds, meters, second, radians
from mathpad.dimensions import Angle

t = "t" * seconds
g = 9.81 * meters / second ** 2
pi = Angle(radians.units, sympy.pi)  # type: ignore


def frac(numerator, denominator):
    return sympy.Rational(numerator, denominator)
