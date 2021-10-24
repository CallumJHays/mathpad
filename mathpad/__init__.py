import sympy

from mathpad.val import *
from mathpad.units import *

from mathpad.units import *
from mathpad.solve import solve, Solution
from mathpad.equation import Equation
from mathpad._quality_of_life import t, g, pi, frac
from mathpad.algebra import subs, simplify, factor, expand
from mathpad.display import tabulate

from mathpad.functions import piecewise, sqrt
from mathpad.calculus import diff, integral
from mathpad.trigonometry import cos, sin, tan, magnitude, hypotenuse
from mathpad.simulate_dynamic_system import simulate_dynamic_system
from mathpad.vec3 import Vec3

try:
    from IPython.display import display
except ImportError:
    pass


sympy.init_printing()  # type: ignore
sympy.printing.printer.Printer.set_global_settings(min=-3, max=4)  # type: ignore

__version__ = "0.1.10"