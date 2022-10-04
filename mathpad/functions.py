from typing import List, Optional, Tuple
from sympy import Piecewise

from mathpad.val import Val, ValT, Q
from mathpad._quality_of_life import frac

# TODO: improve API once ">", "<", ">=" etc operators are implemented for Val
def piecewise(x: Val, region_vals: List[Tuple[float, Q[ValT]]]) -> ValT:
    "a piecewise series of <"
    assert any(region_vals)
    assert region_vals[-1][0] == float("inf")
    inp = []
    prev_val: Optional[ValT] = None
    for lt, val in region_vals:
        rescaled = val.in_units(prev_val) if prev_val is not None else val
        inp.append((rescaled.val, x.val < lt))
        prev_val = val
    
    assert prev_val

    return prev_val.__class__(
        prev_val.units,
        Piecewise(*inp)
    )


def sqrt(x: Q[Val]):
    return x ** frac(1, 2)