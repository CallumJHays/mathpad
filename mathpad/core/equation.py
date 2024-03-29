from typing import Type, Union, overload, Generic, TypeVar, Tuple, Any

import sympy
import sympy.physics.units as su
from sympy import MatrixSymbol, MatrixExpr
from sympy.physics.vector.printing import vlatex

from mathpad.core.val import Val, Q
from mathpad.core.vector import Vector
from mathpad.core.vector_space import VectorSpace
from mathpad.core.matrix import Matrix
from mathpad.core.frame import Frame



T = TypeVar("T", bound=Union[Val, VectorSpace, Matrix])


class Equation(Generic[T]):

    @overload
    def __init__(
        self,
        lhs: "Q[T]",
        rhs: "Q[T]",
    ):
        ...
    
    @overload
    def __init__(
        self,
        lhs: "Vector[T]",
        rhs: "Vector[T]",
    ):
        ...
        
    @overload
    def __init__(
        self,
        lhs: "T",
        rhs: "T",
    ):
        ...

    def __init__(
        self,
        lhs: Union["Q[T]", "Vector[T]", "T"],
        rhs: Union["Q[T]", "Vector[T]", "T"]
    ):
        from mathpad.core import Val, Vector
        
        lhs_is_val = isinstance(lhs, Val)
        rhs_is_val = isinstance(rhs, Val)

        self.units: Union[su.Quantity, Frame[T], Tuple[Frame[Any], Frame[Any]]] = None

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

        elif isinstance(lhs, Vector) or isinstance(rhs, Vector):
            # both are Vector. handle unit conversion and rescaling if necessary.
            assert isinstance(lhs, Vector) and isinstance(rhs, Vector)

            assert lhs.frame == rhs.frame, f"Vectors must be in the same frame to be equated. {lhs.frame} != {rhs.frame}"
            
            # convert rhs into units of lhs, scaling rhs' val if necessary
            self.units = lhs.frame
            self.lhs = lhs
            self.rhs = rhs.in_units(lhs.frame.space.base_units) # type: ignore
        
        else: # matrix equation
            # don't do automatic rescaling for matrixes.
            # shouldn't be necessary most of the time and the user can do it easily if they want.
            assert isinstance(lhs, Matrix) and isinstance(rhs, Matrix)
            assert lhs.left_frame == rhs.left_frame
            assert lhs.right_frame == rhs.right_frame
            self.lhs = lhs
            self.rhs = rhs
            self.units = (lhs.left_frame, lhs.right_frame)
    
    def __getitem__(self, idx: int):
        """
        Get an equation for a single component of a vector equation.
        If the equation is not a vector equation, this will raise an error.
        """
        from mathpad.core import VectorSpace

        assert isinstance(self.units, VectorSpace), "Can only get a component of a vector equation"
        
        return Equation(self.lhs[idx], self.rhs[idx]) # type: ignore

    def __repr__(self):
        return f"{self.lhs._repr(False)} = {self.rhs._repr(False)} {self.units}"

    def as_sympy_eq(self) -> sympy.Equality:
        return sympy.Equality(self.lhs.expr, self.rhs.expr)  # type: ignore

    # def as_units_eq_without_unknowns(self, unknowns: Collection[Val]):
    #     return sympy.Equality(self.lhs.units, self.rhs.units)

    # Rich displays; Ipython etc
    def _repr_latex_(self):
        from mathpad.core.frame import Frame

        # use vlatex because it applies dot notation where possible
        lhs_ltx = vlatex(self.lhs.expr) \
            .replace("- 1.0 ", "-") \
            .replace("\\text{\\textbackslashvec", "\\vec")
        rhs_ltx = vlatex(self.rhs.expr) \
            .replace("- 1.0 ", "-") \
            .replace("\\textbackslashvec", "\\vec")

        units_ltx = self.units._repr_latex_(wrapped=False) if isinstance(self.units, Frame) \
            else "dimensionless" if self.units == 1 \
            else vlatex(self.units)

        spacer_ltx = "\\hspace{1.25em}"

        return f"$$ {lhs_ltx} = {rhs_ltx} {spacer_ltx} {units_ltx} $$"

    def eval(self) -> bool:
        """
        Evaluate the truthyness of the equation.
        """
        
        # convert matrixsymbols to explicit beforehand because sympy can't tell that
        # a + b == O[a[0] + b[0], a[1] + b[1], ...]
        # this appears to be because there is no link between a as a matrix symbol and a[0] as a matrix element
        lhs = self.lhs.expr.as_explicit() if isinstance(self.lhs.expr, (MatrixSymbol, MatrixExpr)) else self.lhs.expr
        rhs = self.rhs.expr.as_explicit() if isinstance(self.rhs.expr, (MatrixSymbol, MatrixExpr)) else self.rhs.expr
    
        # TODO: check if this will affect solve() in any way
        # TODO: what happens if the equation cannot be evaluated?
        res = lhs.doit() == rhs.doit()
        return res

EquationT = TypeVar("EquationT", bound=Equation)