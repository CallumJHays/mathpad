from typing import Optional, Tuple, Union, overload

import sympy
from sympy.physics.units import Quantity
from sympy.tensor.array.array_derivatives import ArrayDerivative

from mathpad.core.val import Val, Q
from mathpad.core import t
# from mathpad.global_options import _global_options
from mathpad.core.vector_space import VectorSpaceT
from mathpad.core.vector import Vector



@overload
def diff(val: Q[Val], order: int = 1, *, wrt: Val = t) -> Val: ...

@overload
def diff(val: Vector[VectorSpaceT], order: int = 1, *, wrt: Val = t) -> Vector[VectorSpaceT]: ...

def diff(
    val: Union[Q[Val], Vector[VectorSpaceT]], order: int = 1, *, wrt: Val = t
) -> Union[Val, Vector[VectorSpaceT]]:
    # TODO: support partial derivatives by passing in a Vec for wrt

    if isinstance(val, Vector):
        out_frame = val.frame / wrt
        vals = list(val)

        if getattr(val.expr, 'is_symbol', False):
            return Vector(out_frame, val.expr.diff((wrt.expr, order)))
        
        return Vector(out_frame, [
            diff(val, wrt=wrt) for val in vals
        ])

    val_units = val.units if isinstance(val, Val) else val
    val_val: sympy.Expr = val.expr if isinstance(val, Val) else sympy.sympify(val)

    new_units = val_units
    for _ in range(order):
        new_units: Quantity = new_units / wrt.units

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
    val: Vector[VectorSpaceT],
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Vector[VectorSpaceT]: ...

def integral(
    val: Union[Q[Val], Vector[VectorSpaceT]],
    *,
    wrt: Val = t,
    between: Optional[Tuple[Q[Val], Q[Val]]] = None
) -> Union[Q[Val], Vector[VectorSpaceT]]:
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
            val.frame * wrt,
            sympy.integrate(val.expr, integrand) # type: ignore
        )

    val_units = val.units if isinstance(val, Val) else val
    val_expr = val.expr if isinstance(val, Val) else Val

    res = Val(
        val_units * wrt.units, # type: ignore
        sympy.integrate(val_expr, integrand)  # type: ignore
    )

    return res
