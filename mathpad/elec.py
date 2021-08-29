# from typing import Annotated as An, get_type_hints

from mathpad import *


@equation
def resistance_resistivity(
    *, R: Q[Impedance], rho: Q[Resistivity], l: Q[Length], A: Q[Area]
):
    "Relate resistance and resistivity"
    return R == rho * l * A
