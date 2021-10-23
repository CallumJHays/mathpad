from typing import List, Optional, Tuple
from sympy import Piecewise

from mathpad.physical_quantity import AbstractPhysicalQuantity, GPhysicalQuantity, Q
from mathpad._quality_of_life import frac

# TODO: improve API once ">", "<", ">=" etc operators are implemented for AbstractPhysicalQuantity
def piecewise(
    x: AbstractPhysicalQuantity, region_vals: List[Tuple[float, Q[GPhysicalQuantity]]]
) -> GPhysicalQuantity:
    "a piecewise series of <"
    assert any(region_vals)
    assert region_vals[-1][0] == float("inf")
    inp = []
    prev_pqty: Optional[AbstractPhysicalQuantity] = None
    for lt, pqty in region_vals:
        rescaled = pqty.in_units(prev_pqty) if prev_pqty is not None else pqty
        inp.append((rescaled.val, x.val < lt))
        prev_pqty = pqty

    return prev_pqty.new(Piecewise(*inp))


def sqrt(x: Q[AbstractPhysicalQuantity]):
    return x ** frac(1, 2)