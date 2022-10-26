try:
    # pre-load required packages if we are running in pyodide.
    # if we don't do this, we get import errors even though the modules are importable from the IPython console.
    import micropip
    micropip.install(['sympy', 'typing_extensions', 'plotly', 'scipy', 'tqdm'])
except ImportError:
    # if micropip isn't available, we're not running in pyodide.
    pass

import sympy

from mathpad.val import *
from mathpad.dimensions import *
from mathpad.units import *

from mathpad.solve import solve, Solution
from mathpad.equation import Equation
from mathpad._quality_of_life import t, pi, i, e, dimensionless, mathpad_constructor
from mathpad.algebra import subs, simplify, factor, expand

from mathpad.functions import piecewise, sqrt
from mathpad.calculus import diff, integral
from mathpad.trigonometry import cos, sin, tan
from mathpad.vector_space import VectorSpace, R2, R3
from mathpad.vector import Vector
from mathpad.matrix import Matrix
from mathpad.simulate_dynamic_system import simulate_dynamic_system
from mathpad.codegen import as_numpy_func

try:
    from IPython.display import display
except ImportError:
    pass


sympy.init_printing()  # type: ignore
sympy.printing.printer.Printer.set_global_settings(min=-3, max=4)  # type: ignore

__version__ = "1.1.0"
