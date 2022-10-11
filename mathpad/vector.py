
from typing import Generic, Sequence, Union, Any, TypeVar
from typing_extensions import Self

from sympy.physics.vector import vlatex
from sympy import MatrixSymbol, Matrix, MatrixExpr

from mathpad.val import DimensionError, SumDimensionsMismatch, Val, Q
from mathpad.vector_space import VectorSpaceT
from mathpad.equation import Equation
from mathpad._quality_of_life import t


class Vec(Generic[VectorSpaceT]):
    """
    A Vector is an instance of a VectorSpace
    """
    
    def __init__(
        self,
        vector_space: VectorSpaceT,
        vals: Union[
            str,
            Sequence[Q[Val]],
            MatrixExpr
        ],
    ):
        self.space = vector_space

        if isinstance(vals, MatrixExpr):
            # vals is the result of a matrix operation. It should be good to use as-is
            self.expr = vals # type: ignore
        
        elif isinstance(vals, str):
            # construct a symbolic vector
            self.expr: MatrixSymbol = MatrixSymbol(vals, len(vector_space.base_units), 1) # type: ignore
        
        else:
            # TODO: make this error message more obviously related to the vector-spaces
            for val, unit in zip(vals, vector_space.base_units):
                if isinstance(val, Val):
                    DimensionError.check(val, unit) # type: ignore

            self.expr: Matrix = Matrix([val.expr if isinstance(val, Val) else val for val in vals]) # type: ignore
    
    def in_units(self, space: VectorSpaceT) -> 'Vec':
        """
        Convert the units of this vector to a different VectorSpace while retaining its true physical value
        """

        return Vec(space, [
            Val(base_units.units, expr).in_units(new_units)
            for expr, base_units, new_units in zip(
                self.expr, # type: ignore
                self.space.base_units,
                space.base_units
            )
        ])
    
    def __eq__(self, other: 'Vec') -> "Equation":
        
        for a, b in zip(self.space.base_units, other.space.base_units):
            SumDimensionsMismatch.check(a, "==", b) # type: ignore

        return Equation(self, other)
    
    def __hash__(self):
        return hash((self.expr, self.space))
    
    def __add__(self, other: Self) -> Self:
        "self + other"

        assert isinstance(other, Vec), \
            f"Cannot add {type(other)} to {type(self)}"

        for a, b in zip(self.space.base_units, other.space.base_units):
            SumDimensionsMismatch.check(a, "==", b) # type: ignore

        assert self.space is other.space, \
            f"Cannot add vectors of different VectorSpaces: {self.space} + {other.space}"
        
        # convert matrixsymbols to explicit beforehand because sympy can't tell that
        # a + b == O[a[0] + b[0], a[1] + b[1], ...]
        # this appears to be because there is no link between a as a matrix symbol and a[0] as a matrix element
        # self_mat = self.val.as_explicit() if isinstance(self.val, MatrixSymbol) else self.val
        # other_mat = other.val.as_explicit() if isinstance(other.val, MatrixSymbol) else other.val
        
        return self.__class__(self.space, self.expr + other.expr) # type: ignore
    
    def __sub__(self, other: Self) -> Self:
        "self - other"
        
        for a, b in zip(self.space.base_units, other.space.base_units):
            SumDimensionsMismatch.check(a, "==", b)

        assert self.space is other.space, \
            f"Cannot subtract vectors of different VectorSpaces: {self.space} - {other.space}"

        return self.__class__(self.space, self.expr - other.expr) # type: ignore
    
    def _repr_latex_(self, wrapped: bool = True):

        # TODO: get vlatex() to display the MatrixSymbol as a \vec{} always
        # vlatex(self.expr) if isinstance(self.expr, MatrixSymbol) else 
        expr_ltx = (
            "\\begin{bmatrix} "
            + " \\\\ ".join(
                # use vlatex because it applies dot notation where possible
                f'{vlatex(el.expr).replace("- 1.0 ", "-")}'
                    if isinstance(el, Val) else str(el)
                for el in self
            )
            + " \\end{bmatrix}"
        )
        
        vectorspace_ltx = self.space._repr_latex_(wrapped=False)
        
        spacer_ltx = "\\hspace{1.25em}"

        full_ltx = f"{expr_ltx} {spacer_ltx} {vectorspace_ltx}"

        return f"$$ {full_ltx} $$" if wrapped else full_ltx
    
    def __iter__(self):
        return (
            Val(unit.units, val)
            for unit, val
            in zip(self.space.base_units, self.expr) # type: ignore
        )
    
    def __len__(self):
        return self.expr.shape[0] # type: ignore
    
    def __getitem__(self, index: int) -> Val:
        return Val(
            self.space.base_units[index].units,
            self.expr[index]
        )
    
    def __neg__(self) -> Self:
        return self.__class__(self.space, -self.expr) # type: ignore
        
    def __abs__(self):
        """
        Returns the norm / magnitude of this vector

        Raises:
            ValueError: if the vector does not have uniform dimensionality (each base_unit in the vector space must be equivalent)
        """
        from mathpad.functions import sqrt

        try:
            norm_squared = sum(val ** 2 for val in self)
        except SumDimensionsMismatch:
            raise ValueError("Cannot take the norm of a vector with non-uniform units")

        return sqrt(norm_squared)
    
    def __mul__(self, other: Q[Val]):
        return Vec(
            (self.space * other) if isinstance(other, Val) else self.space,
            self.expr * (
                other.expr if isinstance(other, Val) else other # type: ignore
            )
        )
    
    def __rmul__(self, other: Q[Val]):
        return self * other
    
    def __truediv__(self, other: Q[Val]):
        return Vec(
            (self.space / other) if isinstance(other, Val) else self.space,
            self.expr / (other.expr if isinstance(other, Val) else other)
        )
    
    def __str__(self) -> str:
        # TODO: make this output more readable for MatrixExpr's
        nl = "\n"
        nltab = "\n\t"
        val_str = f'["{str(self.expr).replace(nl, nltab)}"]' \
            if isinstance(self.expr, (MatrixSymbol, MatrixExpr)) \
            else str([val for val in self.expr])
        return f"{self.space.name}{val_str}"
    
    def _repr(self, _with_units: bool) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return str(self)
    
    # TODO: extend this to higher dimensions and other bases somehow
    # PS: technically cross product is only defined for 3D and 7D, but the concept of orthogonal basis vectors is more general
    # TODO: should this only be defined for R3?
    def cross(self, other: Self) -> 'Vec':
        """
        Cross product of two vectors.

        Args:
            other: The other vector to take the cross product with.
                Must contain the same number of dimensions as this vector.

            out_space: The space to put the result in. Can be a string or a VectorSpace.
                If a string, a new VectorSpace subclass will be created and instantiated with that name.

        Returns:
            A new vector of the output space containing the cross product of the two vectors.
            
        """
        assert len(self) == len(other) == 3, "Cross product is only defined for 3D vectors"

        out_space = self.space * other.space # type: ignore

        # MatrixSymbol doesn't have the .cross() method - convert to explicit (MatrixExpr) first
        self_val = self.expr.as_explicit() if isinstance(self.expr, MatrixSymbol) else self.expr

        return Vec(
            out_space,
            self_val.cross(other.expr) # type: ignore
        )
    
    def dot(self, other: 'Vec[Any]') -> Val:
        "dot product"

        out_units = (
            self.space.base_units[0] * other.space.base_units[0]
        ).units

        self_val_matrix = self.expr if isinstance(self.expr, Matrix) else Matrix(self.expr)
        other_val_matrix = other.expr if isinstance(other.expr, Matrix) else Matrix(other.expr)

        return Val(
            out_units,
            self_val_matrix.dot(other_val_matrix) # type: ignore
        )

    def diff(self, n: int = 1, wrt: Val = t):
        "differentiation"
        
        return Vec(
            self.space / wrt,
            self.expr.diff((wrt.expr, n)) # type: ignore
        )
    
    def integrate(self, wrt: Val = t):
        "integration"

        return Vec(
            self.space * wrt,
            self.expr.integrate(wrt.expr)
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

        if name in self.space.base_names:
            idx = self.space.base_names.index(name)
            return Val(
                self.space.base_units[idx].units,
                self.expr[idx]
            )
            
        else:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name}. "
                f" (base names are {self.space.base_names})"
            )


VecT = TypeVar('VecT', bound=Vec)

def _broken_rtruediv(self: Vec, other: Q[Val]):
    "Make it obvious that this is impossible, but don't let the type checker know this method is implemented"
    assert isinstance(other, Vec), "Can only divide vectors by vectors. Got {other} / {self}"

setattr(Vec, '__rtruediv__', _broken_rtruediv)