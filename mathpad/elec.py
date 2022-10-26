from typing import List
from mathpad import *

@mathpad_constructor
def resistance_resistivity(
    *,
    R: X[Impedance],  # resistance
    rho: X[Resistivity],  # resisitivity
    l: X[Length],  # length of strip
    A: X[Area]  # cross-sectional area of strip (usually very flat, but wide(ish))
) -> Equation:
    "Relate resistance and resistivity"
    return R == rho * l * A


@mathpad_constructor
def ohms_law(
    *,
    R: X[Impedance],  # resistance
    V: X[Voltage],  # voltage
    I: X[Current]  # current
) -> Equation:
    """
    Ohm's law:
    
    V == I * R
    """
    return V == I * R

# TODO: support List[X[Voltage]] in @mathpad_constructor
# @mathpad_constructor
def kerchoffs_voltage_law(
    *,
    producers: List[X[Voltage]],  # voltage sources
    consumers: List[X[Voltage]],  # voltage drops
) -> Equation:
    """
    Kirchoff's voltage law. 

    The sum of voltage sources is equal to the sum of voltage drops.
    
    sum(producers) == sum(consumers)

    """

    assert producers or consumers, "At least one voltage must be specified"

    return sum(producers) == sum(consumers) # type: ignore - assert should prevent both being 0 length lists


# TODO: support List[X[Voltage]] in @mathpad_constructor
# @mathpad_constructor
def kerchoffs_current_law(
    *,
    into: List[X[Current]],  # current into node
    out: List[X[Current]],  # current
) -> Equation:
    """
    Kirchoff's current law. 

    The sum of currents into a node is equal to the sum of currents out of the node.
    
    sum(into) == sum(out)

    """

    assert into or out, "At least one current must be specified"

    return sum(into) == sum(out) # type: ignore - assert should prevent both being 0 length lists