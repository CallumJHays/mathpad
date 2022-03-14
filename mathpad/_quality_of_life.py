import sympy

from mathpad.units import seconds, meters, second, radians
from mathpad.dimensions import Angle
from mathpad.global_options import _global_options

# don't display this symbol on definition
_global_options.ipython_display_symbol_on_definition = False
t = "t" * seconds
_global_options.ipython_display_symbol_on_definition = True

g = 9.81 * meters / second ** 2
pi = Angle(radians.units, sympy.pi)  # type: ignore


def frac(numerator, denominator):
    return sympy.Rational(numerator, denominator)
