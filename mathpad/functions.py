from typing import List, Optional, Tuple
from sympy import Piecewise

from mathpad.val import Val, GOutputVal, Q
from mathpad._quality_of_life import frac

# TODO: improve API once ">", "<", ">=" etc operators are implemented for Val
def piecewise(x: Val, region_vals: List[Tuple[float, Q[GOutputVal]]]) -> GOutputVal:
    "a piecewise series of <"
    assert any(region_vals)
    assert region_vals[-1][0] == float("inf")
    inp = []
    prev_pqty: Optional[Val] = None
    for lt, pqty in region_vals:
        rescaled = pqty.in_units(prev_pqty) if prev_pqty is not None else pqty
        inp.append((rescaled.val, x.val < lt))
        prev_pqty = pqty

    return prev_pqty.new(Piecewise(*inp))


def sqrt(x: Q[Val]):
    return x ** frac(1, 2)