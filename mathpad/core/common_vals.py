import sympy
import inspect
from typing import TYPE_CHECKING, Callable, Union, Generic, TypeVar

from mathpad.core.units import seconds, radians
from mathpad.core.val import Dimensionless, Val
from mathpad.core.dimensions import Angle

if TYPE_CHECKING:
    from mathpad.core.equation import Equation
    from mathpad.core.vector import Vector
    from mathpad.core.matrix import Matrix

# from mathpad.global_options import _global_options

# don't display this symbol on definition
# _global_options.ipython_display_symbol_on_definition = False
t = "t" * seconds
# _global_options.ipython_display_symbol_on_definition = True

pi = Angle(radians.units, sympy.pi)  # type: ignore
i = 1j # imaginary unit
e = Dimensionless(1, sympy.E) # type: ignore
dimensionless = Dimensionless(1, 1)

