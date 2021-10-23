from typing import Iterable, List, Union, overload
from mathpad.val import Val, OutputVal, Q
from mathpad import t
from mathpad.global_options import _global_options
from mathpad.algebra import simplify
import sympy

# TODO: prescale values and units


@overload
def diff(pqty: Q[Val], n: int = 1, *, wrt: Val = t) -> OutputVal:
    ...


@overload
def diff(pqty: Iterable[Q[Val]], n: int = 1, *, wrt: Val = t) -> List[OutputVal]:
    ...


def diff(
    pqty: Union[Q[Val], Iterable[Q[Val]]], n: int = 1, *, wrt: Val = t
) -> Union[OutputVal, List[OutputVal]]:

    if isinstance(pqty, list):
        return [diff(pq, wrt=wrt, n=n) for pq in pqty]

    else:
        res = OutputVal(
            pqty.units / wrt.units, pqty.val.diff((wrt.val, n))  # type: ignore
        )

        if _global_options.auto_simplify:
            res = simplify(res)

        return res


def integral(pqty: Val, wrt: Val = t) -> OutputVal:
    res = OutputVal(
        pqty.units * wrt.units, sympy.integrate(pqty.val, wrt.val)  # type: ignore
    )

    if _global_options.auto_simplify:
        res = simplify(res)

    return res
