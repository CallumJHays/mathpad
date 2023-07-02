
import inspect
from typing import Any, Callable, Generic, TypeVar, Union
from mathpad.core.equation import Equation
from mathpad.core.matrix import Matrix
from mathpad.core.val import Val
from mathpad.core.vector import Vector


MathPadObject = Union[Val, 'Equation', 'Vector', 'Matrix'] # type: ignore
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
        
        return mp_obj._repr_latex_() # type: ignore
    
    def __call__(self, *args: Any, **kwargs: Any) -> T:
        return self.fn(*args, **kwargs)


F = TypeVar("F", bound=Callable) # type: ignore

# lie about the return type so that the function's signature is preserved
def mathpad_constructor(fn: F) -> F:
    "function decorator that adds a _repr_latex_ method to the function so that it can be displayed in IPython"
    return MathPadConstructor(fn) # type: ignore