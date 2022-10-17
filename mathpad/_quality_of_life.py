import sympy
import inspect
from typing import Callable, cast, TypeVar

from mathpad.units import seconds, radians
from mathpad.val import Dimensionless, Val
from mathpad.dimensions import Angle

# from mathpad.global_options import _global_options

# don't display this symbol on definition
# _global_options.ipython_display_symbol_on_definition = False
t = "t" * seconds
# _global_options.ipython_display_symbol_on_definition = True

pi = Angle(radians.units, sympy.pi)  # type: ignore
i = 1j # imaginary unit
e = Dimensionless(1, sympy.E) # type: ignore
dimensionless = Dimensionless(1, 1)



class MathPadConstructor:
    """
    A function decorator that adds a _repr_latex_ method to the function so that
    it can be displayed in IPython.
    """

    def __init__(self, fn):
        self.fn = fn
    
    def _repr_latex_(self):
        "Calls the function with created symbolic values"

        argspec = inspect.signature(self.fn)

        args = {
            # produce a symbolic value for each argument, with base units of that argument's dimension
            param.name: param.name * Val(param.annotation.__args__[0].base_units)
            for param in argspec.parameters.values()
        }
        
        return self.fn(**args)._repr_latex_()
    
    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


F = TypeVar("F", bound=Callable)

def mathpad_constructor(fn: F) -> F:
    "function decorator that adds a _repr_latex_ method to the function so that it can be displayed in IPython"
    return cast(type(fn), MathPadConstructor(fn))