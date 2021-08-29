from typing import TYPE_CHECKING, get_type_hints
import sympy

if TYPE_CHECKING:
    from mathpad.physical_quantity import GPhysicalQuantity, Q


class Equation:
    def __init__(self, lhs: "Q[GPhysicalQuantity]", rhs: "Q[GPhysicalQuantity]"):
        from mathpad.physical_quantity import AbstractPhysicalQuantity

        lhs_is_pqty = isinstance(lhs, AbstractPhysicalQuantity)
        rhs_is_pqty = isinstance(rhs, AbstractPhysicalQuantity)

        assert lhs_is_pqty or rhs_is_pqty

        self.units = lhs.units if lhs_is_pqty else rhs.units  # type: ignore
        pqty_cls = (lhs if lhs_is_pqty else rhs).__class__

        if lhs_is_pqty and rhs_is_pqty:
            # rescale the rhs to match units
            rhs = rhs.in_units(lhs)
            # sanity check
            assert lhs.units == self.units == rhs.units

        self.lhs = lhs if lhs_is_pqty else pqty_cls(self.units, rhs)
        self.rhs: AbstractPhysicalQuantity = (
            rhs if rhs_is_pqty else pqty_cls(self.units, rhs)
        )

    def __repr__(self):
        return f"{self.lhs._repr(False)} = {self.rhs._repr(False)} {self.units}"

    def as_sympy_eq(self) -> sympy.Equality:
        return sympy.Equality(self.lhs.val, self.rhs.val)  # type: ignore

    # def as_units_eq_without_unknowns(self, unknowns: Collection[PhysicalQuantity]):
    #     return sympy.Equality(self.lhs.units, self.rhs.units)


def equation(fn):
    # TODO: check input types and constraints
    def wrap(**kwargs):
        return fn(**kwargs)

    wrap.__name__ = fn.__name__
    wrap.__doc__ = f"{fn.__doc__}\n\n" + "\n".join(
        f"{argname} [{ann.__metadata__[0]}]: {ann.__metadata__[1]}"
        for argname, ann in get_type_hints(fn, include_extras=True).items()
        if argname != "return"
    )
    return wrap
