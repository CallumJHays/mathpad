from typing import TYPE_CHECKING
import sympy
from sympy.physics.vector.printing import vlatex

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

        self.lhs: AbstractPhysicalQuantity = (
            lhs if lhs_is_pqty else pqty_cls(self.units, rhs)
        )
        self.rhs: AbstractPhysicalQuantity = (
            rhs if rhs_is_pqty else pqty_cls(self.units, rhs)
        )

    def __repr__(self):
        return f"{self.lhs._repr(False)} = {self.rhs._repr(False)} {self.units}"

    def as_sympy_eq(self) -> sympy.Equality:
        return sympy.Equality(self.lhs.val, self.rhs.val)  # type: ignore

    # def as_units_eq_without_unknowns(self, unknowns: Collection[PhysicalQuantity]):
    #     return sympy.Equality(self.lhs.units, self.rhs.units)

    # Rich displays; Ipython etc
    def _repr_latex_(self):
        from mathpad.physical_quantity import AbstractPhysicalQuantity

        # use vlatex because it applies dot notation where possible
        lhs_ltx = (
            vlatex(self.lhs.val)
            if isinstance(self.lhs, AbstractPhysicalQuantity)
            else str(self.lhs)
        ).replace("- 1.0 ", "-")

        rhs_ltx = (
            vlatex(self.rhs.val)
            if isinstance(self.rhs, AbstractPhysicalQuantity)
            else str(self.rhs)
        ).replace("- 1.0 ", "-")

        units_ltx = "dimensionless" if self.units == 1 else vlatex(self.units)

        spacer_ltx = "\\hspace{1.25em}"

        return f"$\\displaystyle {lhs_ltx} = {rhs_ltx} {spacer_ltx} {units_ltx}$"
