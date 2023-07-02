
from typing import TYPE_CHECKING, Generic, Iterator, Optional, Sequence, TypeVar, Union, Any
from typing_extensions import Self, Literal

from sympy.physics.vector import vlatex
from sympy.vector import Dot, Vector as SympyVector
from sympy.physics.units.util import convert_to
from sympy.physics.units.unitsystem import UnitSystem
from sympy.tensor.array.array_derivatives import ArrayDerivative
from sympy import Basic, MatrixSymbol, Matrix, MatrixExpr, Expr, Derivative, Function, Symbol

from mathpad.core.val import DimensionError, SumDimensionsMismatchError, Val, Q, _split_coeff_and_units
from mathpad.core.vector_space import VectorSpace, VectorSpaceT, Homogeneous
from mathpad.core.frame import Frame
from mathpad.sympy_extensions import SymbolicMatrixFunction

if TYPE_CHECKING:
    from mathpad.core.equation import Equation

__all__ = ["Vector"]

class Vector(Generic[VectorSpaceT]):
    """
    A Vector is an instance of a VectorSpace
    """
    
    def __init__(
        self,
        frame: Frame[VectorSpaceT],
        expr: Union[Sequence[Q[Val]], MatrixExpr, ArrayDerivative, SymbolicMatrixFunction],
        check: bool = False
    ):
        self.frame = frame

        if isinstance(expr, (MatrixExpr, ArrayDerivative, SymbolicMatrixFunction, self.Cross)):
            # expr is good to use as-is
            self.expr = expr
        
        else: # must be a sequence of Q[Val] - construct a Matrix from it
            assert len(expr) == len(frame.space.base_units), \
                f"Vector must have the same number of elements as the space \"{frame.space.name}\":\n\tExpected {frame.space.base_units}, got {expr}"

            if check:
                # TODO: make this error message more obviously related to the vector-spaces
                for val, unit in zip(expr, frame.space.base_units):
                    if isinstance(val, Val):
                        DimensionError.check(val, unit) # type: ignore

            self.expr \
                = Matrix([val.expr if isinstance(val, Val) else val for val in expr])
    
    def __eq__(self, other: 'Vector') -> "Equation[VectorSpaceT]":
        from mathpad.core.equation import Equation
        
        for a, b in zip(self.frame.space.base_units, other.frame.space.base_units):
            SumDimensionsMismatchError.check(a, "==", b) # type: ignore

        return Equation(self, other)
    
    def __hash__(self):
        return hash((str(self.expr), self.frame.space))
    
    def __add__(self, other: 'Vector[VectorSpaceT]') -> 'Vector[VectorSpaceT]':
        "self + other"

        assert isinstance(other, Vector), \
            f"Cannot add {type(other)} to {type(self)}"

        for a, b in zip(self.frame.space.base_units, other.frame.space.base_units):
            SumDimensionsMismatchError.check(a, "==", b) # type: ignore

        assert self.frame.space is other.frame.space, \
            f"Cannot add vectors of different VectorSpaces: {self.frame.space} + {other.frame.space}"
        
        # convert matrixsymbols to explicit beforehand because sympy can't tell that
        # a + b == O[a[0] + b[0], a[1] + b[1], ...]
        # this appears to be because there is no link between a as a matrix symbol and a[0] as a matrix element
        # self_mat = self.val.as_explicit() if isinstance(self.val, MatrixSymbol) else self.val
        # other_mat = other.val.as_explicit() if isinstance(other.val, MatrixSymbol) else other.val
        
        return self.__class__(self.frame, self.expr + other.expr) # type: ignore
    
    def __sub__(self, other: Self) -> Self:
        "self - other"
        
        for a, b in zip(self.frame.space.base_units, other.frame.space.base_units):
            SumDimensionsMismatchError.check(a, "==", b)

        assert self.frame.space is other.frame.space, \
            f"Cannot subtract vectors of different VectorSpaces: {self.frame.space} - {other.frame.space}"

        return self.__class__(self.frame, self.expr - other.expr) # type: ignore

    def in_units(self, units: Union[Literal["SI"], Sequence[Val]]) -> Self:
        
        if isinstance(units, str):
            assert units == "SI", f"Only 'SI' is supported. Got {units}"
            target_units = [
                UnitSystem.get_unit_system(unit)._base_units
                for unit in units
            ]

        else:
            assert all(unit.expr == 1 for unit in units), \
                f"valid units must have an expr == 1. Got {units}"
            
            target_units = units
        
        scaling_factors, new_units = zip(*(
            _split_coeff_and_units(
                convert_to(self_unit.units, target_units.units)  # type: ignore
            )
            for self_unit, target_units in zip(self.frame.space.base_units, target_units)
        ))

        if all(sf == 1 for sf in scaling_factors):
            return self.__class__(self.frame, self.expr)

        scaling_factors_vec = Matrix(scaling_factors)

        new_expr = scaling_factors_vec * self.expr

        new_space = VectorSpace(
            self.frame.space.name,
            self.frame.space.base_names,
            new_units
        )
        
        frame = new_space(self.frame.name)

        return self.__class__(frame, new_expr)
    
    def _repr_latex_(self, wrapped: bool = True):

        # TODO: get vlatex() to display the MatrixSymbol as a \vec{} always
        # vlatex(self.expr) if isinstance(self.expr, MatrixSymbol) else``
        
        if isinstance(self.expr, Derivative):
            # workaround for vlatex() crashing on vector derivatives.
            orig_expr_variables = self.expr.__class__.variables
            self.expr.__class__.variables = self.expr._wrt_variables # type: ignore
        else:
            orig_expr_variables = None

        expr_ltx = (
            "\\begin{bmatrix}"
            + " \\\\ ".join(
                # use vlatex because it applies dot notation where possible
                f'{vlatex(el.expr).replace("- 1.0 ", "-")}'
                    if isinstance(el, Val) else str(el)
                for el in self
            )
            + " \\end{bmatrix}"
        ) if isinstance(self.expr, Matrix) else vlatex(self.expr)
    
        if orig_expr_variables:
            # undo temp monkeypatch
            self.expr.__class__.variables = orig_expr_variables # type: ignore

        frame_ltx = self.frame._repr_latex_(wrapped=False)
        
        spacer_ltx = "\\hspace{1.25em}"

        full_ltx = f"{expr_ltx} {spacer_ltx} {frame_ltx}"

        return f"$$ {full_ltx} $$" if wrapped else full_ltx
    
    def __iter__(self) -> Iterator[Val]:
        return (
            self[index] for index in range(len(self)) # type: ignore
        )
    
    def __len__(self):
        return self.expr.shape[0] # type: ignore
    
    def __getitem__(self, index: int) -> Val:
        unit = self.frame.space.base_units[index].units
        # base_name = self.frame.space.base_names[index]

        # expr: Basic = Symbol(f"{self.expr.name}_{base_name}") \
        #     if getattr(self.expr, 'is_symbol', False) \
        #     else self.expr[index] # type: ignore
        
        return Val(unit, self.expr[index]) # type: ignore
    
    def __neg__(self) -> Self:
        return self.__class__(self.frame.space, -self.expr) # type: ignore
        
    def norm(self) -> Val:
        """
        Returns the norm / magnitude of this vector

        Raises:
            ValueError: if the vector does not have uniform dimensionality (each base_unit in the vector space must be equivalent)
        """
        from mathpad.maths.functions import sqrt

        assert len(set(self.frame.space.base_units)) == 1, "Cannot take the norm of a vector with non-uniform units"

        return Val(
            self.frame.space.base_units[0].units,
            self.expr.norm() if isinstance(self.expr, MatrixSymbol) \
                else sqrt(sum(el ** 2 for el in self)).expr
        )
    
    def __mul__(self, other: Q[Val]):
        return Vector(
            (self.frame * other) if isinstance(other, Val) else self.frame,
            self.expr * (
                other.expr if isinstance(other, Val) else other # type: ignore
            )
        )
    
    def __rmul__(self, other: Q[Val]):
        return self * other
    
    def __truediv__(self, other: Q[Val]):
        return Vector(
            (self.frame / other) if isinstance(other, Val) else self.frame,
            self.expr / (other.expr if isinstance(other, Val) else other)
        )
    
    def __str__(self) -> str:
        # TODO: make this output more readable for MatrixExpr's
        nl = "\n"
        nltab = "\n\t"
        val_str = f'{str(self.expr).replace(nl, nltab)}' \
            if isinstance(self.expr, Expr) \
            else str([val for val in self.expr])

        return f"{val_str} wrt. {self.frame.name}" if self.frame.name else val_str
    
    def _repr(self, _with_units: bool) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return str(self)
    
    def eval(self, precision: int = 6):
        "Return a new Vec with consts evaluated to their floating point equivalent with given precision"
        return self.__class__(self.frame.space, self.expr.evalf(precision))
    
    # TODO: extend this to higher dimensions and other bases somehow
    # PS: technically cross product is only defined for 3D and 7D, but the concept of orthogonal basis vectors is more general
    # TODO: should this only be defined for R3?
    def cross(self, other: Self) -> 'Vector[Any]':
        """
        Cross product of two vectors.

        Args:
            other: The other vector to take the cross product with.
                Must contain the same number of dimensions as this vector.

        Returns:
            A new vector of the output space containing the cross product of the two vectors.
            
        """
        assert len(self) == len(other) == 3, "Cross product is only defined for 3D vectors"

        out_space = self.frame.space * other.frame.space # type: ignore
        out_frame = out_space(self.frame.name)

        # MatrixSymbol doesn't have the .cross() method - convert to explicit (MatrixExpr) first
        self_val = self.expr.as_explicit() if isinstance(self.expr, MatrixSymbol) else self.expr

        return Vector(
            out_frame,
            self.Cross(self_val, other.expr) # type: ignore
        )
    
    def dot(self, other: 'Vector[Any]') -> Val:
        "dot product"

        out_units = (
            self.frame.space.base_units[0] * other.frame.space.base_units[0]
        ).units

        self_val_matrix = self.expr if isinstance(self.expr, Matrix) else Matrix(self.expr)
        other_val_matrix = other.expr if isinstance(other.expr, Matrix) else Matrix(other.expr)

        return Val(
            out_units,
            self.Dot(self_val_matrix, other_val_matrix)
        )
    
    def __getattr__(self, name: str) -> Val:
        """
        Construct a vector from a base name, with a value of 1 in the direction of the base.

        For example, the R3 VectorSpace has the base_names: ('i', 'j', 'k').
        Resulting in the following behavior:

        >>> R3.i == R3[1, 0, 0]
        True

        >>> R3.j == R3[0, 1, 0]
        True

        etc.

        """

        if name in self.frame.space.base_names:
            idx = self.frame.space.base_names.index(name)
            return self[idx]
            
        else:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name}. "
                f" (base names are {self.frame.space.base_names})"
            )
    
    def homogeneous(self, name: Optional[str] = None) -> 'Vector[Homogeneous[VectorSpaceT]]':
        "Return a new vector with an extra dimension of 1"
        return Vector(
            Frame(self.frame.space.homogeneous(name), f"self.frame.name", wrt=None),
            self.expr.row_insert(len(self.frame.space), Matrix([1])) # type: ignore
        )
        
    class Cross(SympyVector):
        """
        A custom Cross product class that works with matrices instead of vectors.
        Also gets rid of some weird negation behaviour (see sympy.vector.vector.Cross's __new__ method)
        """
            
        def __new__(cls, expr1, expr2):
            obj = Expr.__new__(cls, expr1, expr2)
            obj._expr1 = expr1 # type: ignore - these are referenced in printing
            obj._expr2 = expr2 # type: ignore
            return obj

        def doit(self, **hints):
            a, b = self.args # type: ignore
            return a.cross(b, **hints) # type: ignore


    class Dot(Dot):
        """
        A custom Dot product class that works with matrices instead of vectors
        """

        def doit(self, **hints):
            return self._expr1.dot(self._expr2, **hints) # type: ignore



VecT = TypeVar('VecT', bound=Vector)

from mathpad.sympy_extensions.monkeypatch import monkeypatch_method

@monkeypatch_method(Vector)
def __rtruediv__(self: Vector[Any], other: Q[Val]):
    "[UNAVAILABLE] Display helfpul error message, without letting the type checker know"
    assert isinstance(other, Vector), f"Can only divide vectors by vectors. Got {other} / {self}"

