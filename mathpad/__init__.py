try:
    # pre-load required packages if we are running in pyodide.
    # if we don't do this, we get import errors even though the modules are importable from the IPython console.
    import micropip
    micropip.install(['sympy', 'typing_extensions', 'plotly', 'scipy', 'tqdm'])
except ImportError:
    # if micropip isn't available, we're not running in pyodide.
    pass

import sympy

from mathpad.core import *
from mathpad.maths import *

from mathpad.library.mathpad_constructor import mathpad_constructor
from mathpad.simulate_dynamic_system import simulate_dynamic_system

import mathpad.codegen

try:
    from IPython.display import display
except ImportError:
    pass


sympy.init_printing()  # type: ignore
sympy.printing.printer.Printer.set_global_settings(min=-3, max=4)  # type: ignore

__version__ = "2.1.0"
