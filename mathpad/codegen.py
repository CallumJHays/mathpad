

from typing import Any, Callable, ItemsView, KeysView, TypeVar, Union, ValuesView
from typing_extensions import Protocol
from sympy.utilities.lambdify import lambdify
import numpy
from numpy.typing import ArrayLike, NDArray

from mathpad.val import Num, Val, ValT
from mathpad.vector import Vector

__all__ = ["as_numpy_func"]


# Until a contravariant Map type is added to typing, we have to use this
# https://github.com/python/typing_extensions/issues/5#issue-1241825018

ArrayOrNum = TypeVar("ArrayOrNum", bound=Union[Num, ArrayLike], covariant=True)

class ArgMap(Protocol[ValT, ArrayOrNum]):
    def keys(self) -> KeysView[ValT]: ...
    def items(self) -> ItemsView[ValT, ArrayOrNum]: ...
    def values(self) -> ValuesView[ArrayOrNum]: ...


def as_numpy_func(val: Val) -> Callable[[ArgMap[Val, ArrayLike]], NDArray[Any]]:
    """
    Convert a Val or Vec to an efficient numpy function.
    """

    if isinstance(val, Vector):
        raise NotImplementedError("TODO: implement Vec")

    syms = list(val.expr.free_symbols)
    fn = lambdify(syms, val.expr)

    def numpy_func(arg_map: ArgMap[Val, Union[Num, ArrayLike]]) -> Union[NDArray[Any], Num]:
        
        vals = [None] * len(syms)
        for val, num_or_arr in arg_map.items():
            idx = syms.index(val.expr)
            vals[idx] = num_or_arr # type: ignore
        return fn(*[numpy.array(val) for val in vals])

    return numpy_func # type: ignore