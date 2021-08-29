import sympy

from .physical_quantity import *
from .physical_quantities import *

from .units import *
from .solve import solve, Solution
from .equation import equation, Equation
from .var import var

sympy.printing.printer.Printer.set_global_settings(min=-3, max=4)  # type: ignore
sympy.init_printing(True, use_unicode=True, use_latex=True)  # type: ignore