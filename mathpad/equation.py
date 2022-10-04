from typing import TYPE_CHECKING, Type, TypeVar, Union, overload

import sympy
from sympy import MatrixSymbol, MatrixExpr
from sympy.physics.vector.printing import vlatex

if TYPE_CHECKING:
    from mathpad.val import ValT, Q
    from mathpad.vector import VecT


class Equation:

    @overload
    def __init__(
        self,
        lhs: "Q[ValT]",
        rhs: "Q[ValT]",
    ):
        ...
    
    @overload
    def __init__(
        self,
        lhs: "VecT",
        rhs: "VecT",
    ):
        ...

    def __init__(
        self,
        lhs: Union["Q[ValT]", "VecT"],
        rhs: Union["Q[ValT]", "VecT"]
    ):
        from mathpad.val import Val
        from mathpad.vector import Vec
        
        lhs_is_val = isinstance(lhs, Val)
        rhs_is_val = isinstance(rhs, Val)

        if lhs_is_val or rhs_is_val:
            # one of them is a Val. The other is either a Val or a Num
            
            if lhs_is_val and rhs_is_val:
                # both are Val. handle unit conversion and rescaling if necessary.

                # convert rhs into units of lhs, scaling rhs' val if necessary
                rhs = rhs.in_units(lhs)

            val_cls: Type[Val] = (lhs if lhs_is_val else rhs).__class__ # type: ignore
            self.units = lhs.units if lhs_is_val else rhs.units # type: ignore
            self.lhs = lhs if lhs_is_val else val_cls(self.units, lhs) # type: ignore
            self.rhs = rhs if rhs_is_val else val_cls(self.units, rhs) # type: ignore

            assert self.lhs.units == self.units == self.rhs.units # type: ignore - sanity check

        else:
            # both are Vector. handle unit conversion and rescaling if necessary.
            assert isinstance(lhs, Vec) and isinstance(rhs, Vec)
            
            # convert rhs into units of lhs, scaling rhs' val if necessary
            self.units = lhs.space
            self.lhs = lhs
            self.rhs: Union[VecT, ValT] = rhs.in_units(lhs.space)

    def __repr__(self):
        return f"{self.lhs._repr(False)} = {self.rhs._repr(False)} {self.units}"

    def as_sympy_eq(self) -> sympy.Equality:
        return sympy.Equality(self.lhs.val, self.rhs.val)  # type: ignore

    # def as_units_eq_without_unknowns(self, unknowns: Collection[Val]):
    #     return sympy.Equality(self.lhs.units, self.rhs.units)

    # Rich displays; Ipython etc
    def _repr_latex_(self):
        from mathpad.val import Val

        # use vlatex because it applies dot notation where possible
        lhs_ltx = (
            vlatex(self.lhs.val) if isinstance(self.lhs, Val) else str(self.lhs)
        ).replace("- 1.0 ", "-")

        rhs_ltx = (
            vlatex(self.rhs.val) if isinstance(self.rhs, Val) else str(self.rhs)
        ).replace("- 1.0 ", "-")

        units_ltx = "dimensionless" if self.units == 1 else vlatex(self.units)

        spacer_ltx = "\\hspace{1.25em}"

        return f"$$ {lhs_ltx} = {rhs_ltx} {spacer_ltx} {units_ltx} $$"

    def eval(self) -> bool:
        """
        Evaluate the truthyness of the equation.
        """
        
        # convert matrixsymbols to explicit beforehand because sympy can't tell that
        # a + b == O[a[0] + b[0], a[1] + b[1], ...]
        # this appears to be because there is no link between a as a matrix symbol and a[0] as a matrix element
        lhs = self.lhs.val.as_explicit() if isinstance(self.lhs.val, (MatrixSymbol, MatrixExpr)) else self.lhs.val
        rhs = self.rhs.val.as_explicit() if isinstance(self.rhs.val, (MatrixSymbol, MatrixExpr)) else self.rhs.val
    
        # TODO: check if this will affect solve() in any way
        return lhs == rhs