import sympy
import inspect
from typing import TYPE_CHECKING, Callable, Union, Generic, TypeVar

from mathpad.units import seconds, radians
from mathpad.val import Dimensionless, Val
from mathpad.dimensions import Angle

if TYPE_CHECKING:
    from mathpad.equation import Equation
    from mathpad.vector import Vector
    from mathpad.matrix import Matrix

# from mathpad.global_options import _global_options

# don't display this symbol on definition
# _global_options.ipython_display_symbol_on_definition = False
t = "t" * seconds
# _global_options.ipython_display_symbol_on_definition = True

pi = Angle(radians.units, sympy.pi)  # type: ignore
i = 1j # imaginary unit
e = Dimensionless(1, sympy.E) # type: ignore
dimensionless = Dimensionless(1, 1)

MathPadObject = Union[Val, 'Equation', 'Vector', 'Matrix']
T = TypeVar("T", bound=MathPadObject)

class MathPadConstructor(Generic[T]):
    """
    A function decorator that adds a _repr_latex_ method to the function so that
    it can be displayed in IPython.
    """

    def __init__(self, fn: Callable[..., T]):
        self.fn = fn
    
    def _repr_latex_(self):
        "Calls the function with created symbolic values to produce a LaTeX representation"

        argspec = inspect.signature(self.fn)

        arg2dimension = {
            # produce a symbolic value for each argument, with base units of that argument's dimension
            param.name: param.annotation.__args__[0]
            for param in argspec.parameters.values()
        }

        args = {
            # produce a symbolic value for each argument, with base units of that argument's dimension
            pname: pname * Val(dimension.base_units)
            for pname, dimension in arg2dimension.items()
        }

        argspec_str = ", ".join(f"{pname}: {dimension.__name__}" for pname, dimension in arg2dimension.items())

        # TODO: parse the type signature to determine what parameters are kwargs only rather than assume all are
        print(f"{self.fn.__name__}(*, {argspec_str})")

        # print the docstr if we have one
        if self.fn.__doc__:
            # hide the example section if it exists
            pre_example_docstr, *_ = self.fn.__doc__.split("Example:")
            print(pre_example_docstr.rstrip())

        mp_obj = self.fn(**args)
        
        return mp_obj._repr_latex_()
    
    def __call__(self, *args, **kwargs) -> T:
        return self.fn(*args, **kwargs)


F = TypeVar("F", bound=Callable)

# lie about the return type so that the function's signature is preserved
def mathpad_constructor(fn: F) -> F:
    "function decorator that adds a _repr_latex_ method to the function so that it can be displayed in IPython"
    return MathPadConstructor(fn) # type: ignore