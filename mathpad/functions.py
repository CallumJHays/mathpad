from typing import List, Optional, Tuple, overload
from sympy import Piecewise

from mathpad.val import Dimensionless, Num, Val, ValT, Q

# TODO: improve API once ">", "<", ">=" etc operators are implemented for Val
def piecewise(x: Val, region_vals: List[Tuple[float, Q[ValT]]]) -> ValT:
    "a piecewise series of <"
    assert any(region_vals)
    assert region_vals[-1][0] == float("inf")
    inp = []
    prev_val: Optional[ValT] = None
    for lt, val in region_vals:
        rescaled = val.in_units(prev_val) if prev_val is not None else val
        inp.append((rescaled.expr, x.expr < lt))
        prev_val = val
    
    assert prev_val

    return prev_val.__class__(
        prev_val.units,
        Piecewise(*inp)
    )

@overload
def sqrt(x: Num) -> Num:
    ...

@overload
def sqrt(x: Val) -> Val:
    ...

def sqrt(x: Q[Val]) -> Q[Val]:
    from sympy import sqrt as _sqrt
    return Val(x.units**0.5, _sqrt(x.expr))