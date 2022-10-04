from typing import Union
from ansitable import ANSITable
from mathpad.val import Val
from mathpad.equation import Equation


def tabulate(*entities: Union[Val, Equation]):
    "Prints a list of values or relations consistent with the display environment"

    # TODO: latex version in supporting IPython environments
    table = ANSITable("  Entity  ", "  Units  ", border="thick", bordercolor="blue")

    for entity in entities:
        if isinstance(entity, Val):
            table.row(entity.val, entity.units)

        else:
            table.row(f"{entity.lhs} == {entity.rhs}", entity.units)

    table.print()