from typing import Optional, Tuple, Union, overload

import sympy

from mathpad.val import Val, Q
from mathpad import t
# from mathpad.global_options import _global_options
from mathpad.algebra import simplify
from mathpad.vector_space import VectorSpace
from mathpad.vector import Vector



# TODO: prescale values and units IF NECESSARY

@overload
def diff(val: Q[Val], order: int = 1, *, wrt: Val = t) -> Val: ...

@overload
def diff(val: Vector, order: int = 1, *, wrt: Val = t) -> Vector: ...

def diff(
    val: Union[Q[Val], Vector], order: int = 1, *, wrt: Val = t
) -> Union[Val, Vector]:
    # TODO: support partial derivatives by passing in a Vec for wrt

    if isinstance(val, Vector):
        return Vector(
            val.space / wrt,
            val.expr.diff((wrt.expr, order)) # type: ignore
        )

    val_units = val.units if isinstance(val, Val) else val
    val_val = val.expr if isinstance(val, Val) else sympy.sympify(val)

    new_units = val_units
    for _ in range(order):
        new_units = new_units / wrt.units

    res = Val(
        new_units, # type: ignore
        val_val.diff((wrt.expr, order))  # type: ignore
    )

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
    val: Vector,
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Vector: ...

def integral(
    val: Union[Q[Val], Vector],
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Union[Q[Val], Vector]:
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

    integrand = (wrt.expr, *between) if between else wrt.expr 

    if isinstance(val, Vector):
        return Vector(
            val.space * wrt,
            sympy.integrate(val.expr, integrand) # type: ignore
        )

    val_units = val.units if isinstance(val, Val) else val
    val_expr = val.expr if isinstance(val, Val) else Val

    res = Val(
        val_units * wrt.units, # type: ignore
        sympy.integrate(val_expr, integrand)  # type: ignore
    )

    return res
