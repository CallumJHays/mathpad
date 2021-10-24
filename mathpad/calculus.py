from typing import Iterable, List, Union, overload
from mathpad.val import Val, OutputVal, Q
from mathpad import t
from mathpad.global_options import _global_options
from mathpad.algebra import simplify
import sympy

# TODO: prescale values and units


@overload
def diff(val: Q[Val], n: int = 1, *, wrt: Val = t) -> OutputVal:
    ...


@overload
def diff(val: Iterable[Q[Val]], n: int = 1, *, wrt: Val = t) -> List[OutputVal]:
    ...


def diff(
    val: Union[Q[Val], Iterable[Q[Val]]], n: int = 1, *, wrt: Val = t
) -> Union[OutputVal, List[OutputVal]]:

    try:  # is val iterable? assume its a vector
        iter(val)
        return [diff(pq, wrt=wrt, n=n) for pq in val]

    except TypeError:
        res = OutputVal(
            val.units / wrt.units, val.val.diff((wrt.val, n))  # type: ignore
        )

        if _global_options.auto_simplify:
            res = simplify(res)

        return res


def integral(val: Val, wrt: Val = t) -> OutputVal:
    res = OutputVal(
        val.units * wrt.units, sympy.integrate(val.val, wrt.val)  # type: ignore
    )

    if _global_options.auto_simplify:
        res = simplify(res)

    return res
