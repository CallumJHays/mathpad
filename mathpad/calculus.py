from typing import Optional, Tuple, Union, overload

import sympy

from mathpad.val import Val, Q
from mathpad import t
from mathpad.global_options import _global_options
from mathpad.algebra import simplify
from mathpad.vector_space import VectorSpace
from mathpad.vector import Vec



# TODO: prescale values and units IF NECESSARY

@overload
def diff(val: Q[Val], order: int = 1, *, wrt: Val = t) -> Val: ...

@overload
def diff(val: Vec, order: int = 1, *, wrt: Val = t) -> Vec: ...

def diff(
    val: Union[Q[Val], Vec], order: int = 1, *, wrt: Val = t
) -> Union[Val, Vec]:
    # TODO: support partial derivatives by passing in a Vec for wrt

    if isinstance(val, Vec):
        out_space = val.space / wrt
        return Vec(out_space, [diff(v, order, wrt=wrt) for v in val])

    val_units = val.units if isinstance(val, Val) else val
    val_val = val.val if isinstance(val, Val) else sympy.sympify(val)

    new_units = val_units
    for _ in range(order):
        new_units = new_units / wrt.units

    res = Val(
        new_units, # type: ignore
        val_val.diff((wrt.val, order))  # type: ignore
    )

    if _global_options.auto_simplify:
        res = simplify(res)

    return res

@overload
def integral(
    val: Q[Val],
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Val: ...

@overload
def integral(
    val: Vec,
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Vec: ...

def integral(
    val: Union[Q[Val], Vec],
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Union[Q[Val], Vec]:
    """
    Integrate a value with respect to a symbolic Val.

    Arguments:

        val: the value to integrate

        wrt: the variable to integrate with respect to

        between: a tuple of values. If provided, the definite integral will be returned.
    
    Returns:

        The indefinite integral of `val` with respect to `wrt`, or the definite integral
        between `between[0]` and `between[1]` if `between` is provided.
    
    Examples:

        >>> integral(2 * t ** 2)
        2*t**3/3
        >>> integral(2 * t ** 2, between=(0, 1))
        2/3

        >>> x = "x(t)" * meters
        >>> integral(x, wrt=t)
        x(t)*t
        >>> integral(x, wrt=t, between=(0, 1))
        x(1) - x(0)

        >>> y = "y" * meters
        >>> integral(y, wrt=t**2)
        y*t
        >>> integral(y, wrt=t, between=(0, 1))
        y
    
    """

    if isinstance(val, Vec):
        return Vec(
            val.space * wrt,
            [integral(v, wrt=wrt, between=between) for v in val]
        )

    val_units = val.units if isinstance(val, Val) else val
    val_val = val.val if isinstance(val, Val) else Val

    integrand = (wrt.val, *between) if between else wrt.val 

    res = Val(
        val_units * wrt.units, # type: ignore
        sympy.integrate(val_val, integrand)  # type: ignore
    )

    if _global_options.auto_simplify:
        res = simplify(res)

    return res
