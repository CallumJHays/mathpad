# from typing import Annotated as An, get_type_hints

from mathpad import *


@equation
def resistance_resistivity(
    *,
    R: Q[Impedance],  # resistance
    rho: Q[Resistivity],  # resisitivity
    l: Q[Length],  # length of strip
    A: Q[Area]  # cross-sectional area of strip (usually very flat, but wide(ish))
):
    "Relate resistance and resistivity"
    return R == rho * l * A
