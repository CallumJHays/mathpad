from typing import Union
from ansitable import ANSITable
from mathpad.physical_quantity import AbstractPhysicalQuantity
from mathpad.equation import Equation


def tabulate(*entities: Union[AbstractPhysicalQuantity, Equation]):
    "Prints a list of values or relations consistent with the display environment"

    # TODO: latex version in supporting IPython environments
    table = ANSITable("  Entity  ", "  Units  ", border="thick", bordercolor="blue")

    for entity in entities:
        if isinstance(entity, AbstractPhysicalQuantity):
            table.row(entity.val, entity.units)

        else:
            table.row(f"{entity.lhs} == {entity.rhs}", entity.units)

    table.print()