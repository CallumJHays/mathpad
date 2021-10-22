from typing import Iterable, List, Union, overload
from mathpad.physical_quantity import AbstractPhysicalQuantity, PhysicalQuantity, Q
from mathpad import t
from mathpad.global_options import _global_options
from mathpad.algebra import simplify
import sympy

# TODO: prescale values and units

AnyQty = Q[AbstractPhysicalQuantity]


@overload
def diff(
    pqty: AnyQty, wrt: AbstractPhysicalQuantity = t, n: int = 1
) -> PhysicalQuantity:
    ...


@overload
def diff(
    pqty: Iterable[AnyQty], wrt: AbstractPhysicalQuantity = t, n: int = 1
) -> List[PhysicalQuantity]:
    ...


def diff(
    pqty: Union[AnyQty, Iterable[AnyQty]],
    wrt: AbstractPhysicalQuantity = t,
    n: int = 1
) -> Union[PhysicalQuantity, List[PhysicalQuantity]]:

    if n > 1:
        pqty = diff(pqty, wrt=wrt, n=n-1)

    if isinstance(pqty, list):
        return [diff(pq, wrt=wrt, n=n) for pq in pqty]

    else:
        res = PhysicalQuantity(
            pqty.units / wrt.units, pqty.val.diff(wrt.val)  # type: ignore
        )

        if _global_options.auto_simplify:
            res = simplify(res)

        return res


def integral(
    pqty: AbstractPhysicalQuantity, wrt: AbstractPhysicalQuantity = t
) -> PhysicalQuantity:
    res = PhysicalQuantity(
        pqty.units * wrt.units, sympy.integrate(pqty.val, wrt.val)  # type: ignore
    )

    if _global_options.auto_simplify:
        res = simplify(res)

    return res
