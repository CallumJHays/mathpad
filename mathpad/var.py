from typing import Any, Sequence

import sympy

from mathpad.physical_quantity import GPhysicalQuantity


def var(name: str, unit: GPhysicalQuantity, **assumptions: Any) -> GPhysicalQuantity:
    sym = sympy.Symbol(name, **assumptions)
    return unit.__class__(unit.units, sym)
