import sympy

from .physical_quantity import *
from .physical_quantities import *

from .units import *
from .solve import solve, Solution
from .equation import Equation
from ._quality_of_life import t, g, pi, frac
from .algebra import subs, simplify, factor, expand
from .display import tabulate

from .functions import piecewise, sqrt
from .calculus import diff, integral
from .trigonometry import cos, sin, tan, magnitude, hypotenuse
from .simulate_dynamic_system import simulate_dynamic_system

try:
    from IPython.display import display
except ImportError:
    pass


sympy.init_printing()  # type: ignore
sympy.printing.printer.Printer.set_global_settings(min=-3, max=4)  # type: ignore

__version__ = "0.1.4"