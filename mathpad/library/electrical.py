from typing import List
from mathpad.core import *
from .mathpad_constructor import mathpad_constructor

@mathpad_constructor
def resistance_resistivity(
    *,
    R: Q[Impedance],  # resistance
    rho: Q[Resistivity],  # resisitivity
    l: Q[Length],  # length of strip
    A: Q[Area]  # cross-sectional area of strip (usually very flat, but wide(ish))
) -> Equation[Resistivity]:
    "Resistance and resistivity of a strip of material"
    return R == rho * l * A


@mathpad_constructor
def ohms_law(
    *,
    R: Q[Impedance],  # resistance
    V: Q[Voltage],  # voltage
    I: Q[Current]  # current
) -> Equation[Voltage]:
    """
    Ohm's law:
    
    V == I * R
    """
    return V == I * R

# TODO: support List[Q[Voltage]] in @mathpad_constructor
# @mathpad_constructor
def kerchoffs_voltage_law(
    *,
    producers: List[Q[Voltage]],  # voltage sources
    consumers: List[Q[Voltage]],  # voltage drops
) -> Equation[Voltage]:
    """
    Kirchoff's voltage law. 

    The sum of voltage sources is equal to the sum of voltage drops.
    
    sum(producers) == sum(consumers)

    """

    assert producers or consumers, "At least one voltage must be specified"

    return sum(producers) == sum(consumers) # type: ignore - assert should prevent both being 0 length lists


# TODO: support List[Q[Voltage]] in @mathpad_constructor
# @mathpad_constructor
def kerchoffs_current_law(
    *,
    into: List[Q[Current]],  # current into node
    out: List[Q[Current]],  # current
) -> Equation[Current]:
    """
    Kirchoff's current law. 

    The sum of currents into a node is equal to the sum of currents out of the node.
    
    sum(into) == sum(out)

    """

    assert into or out, "At least one current must be specified"

    return sum(into) == sum(out) # type: ignore - assert should prevent both being 0 length lists