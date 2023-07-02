

from typing import Any, Callable, ItemsView, KeysView, Sequence, TypeVar, Union, ValuesView
from typing_extensions import Protocol
from sympy.utilities.lambdify import lambdify
import numpy
from numpy.typing import ArrayLike, NDArray
from mathpad.core.matrix import Matrix

from mathpad.core.val import Num, Val, ValT
from mathpad.core.vector import Vector

__all__ = ["as_numpy_func"]


# Until a contravariant Map type is added to typing, we have to use this
# https://github.com/python/typing_extensions/issues/5#issue-1241825018

ArrayOrNum = TypeVar("ArrayOrNum", bound=Union[Num, ArrayLike], covariant=True)

class ArgMap(Protocol[ValT, ArrayOrNum]):
    def keys(self) -> KeysView[ValT]: ...
    def items(self) -> ItemsView[ValT, ArrayOrNum]: ...
    def values(self) -> ValuesView[ArrayOrNum]: ...


def as_numpy_func(val: Val) -> Callable[[ArgMap[Val, Union[ArrayLike, Sequence[Val]]]], NDArray[Any]]:
    """
    Convert a Val or Vec to an efficient numpy function.
    """

    if isinstance(val, Vector):
        raise NotImplementedError("TODO: implement Vec")

    syms = list(val.expr.free_symbols)
    fn = lambdify(syms, val.expr)

    def numpy_func(arg_map: ArgMap[Val, Union[ArrayLike, Sequence[Val]]]) -> NDArray[Any]:
        
        vals = [None] * len(syms)
        for val, arr_or_vals in arg_map.items():
            idx = syms.index(val.expr)
            vals[idx] = arr_or_vals # type: ignore
        return fn(*[numpy.array(val) for val in vals])

    return numpy_func # type: ignore


def generate_c_code(
    expr: Union[Val, Vector[Any], Matrix[Any, Any]],
    args: Sequence[Union[Val, Vector[Any], Matrix[Any, Any]]]
) -> str:
    from sympy.utilities.codegen import codegen, CCodeGen

    sympy_args = []
    for arg in args:
        assert arg.expr.is_Symbol
        sympy_args.append(arg.expr)
    
    (_, c_code), (_, _) = codegen(
        [("ans", expr.expr)],
        argument_sequence=sympy_args,
        code_gen=CCodeGen(cse=True))
    c_code: str

    return c_code.split('#include <math.h>')[1]