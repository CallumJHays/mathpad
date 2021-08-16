import sympy
from typing import Any

# from ._expr import Expr
from .physical_quantity import *
from .physical_quantities import *
from .units import *
from .solve import solve
from ._relation import relation

sympy.init_printing(True, use_unicode=True, use_latex=True)  # type: ignore


def var(name: str, unit: GPhysicalQuantity, **assumptions: Any) -> GPhysicalQuantity:
    sym = sympy.Symbol(name, **assumptions)
    return unit.__class__(unit.units, sym, unit.dimension)
