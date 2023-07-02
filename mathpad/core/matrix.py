

from typing import TYPE_CHECKING, Any, Generic, Iterator, List, Sequence, Tuple, TypeVar, Union, overload
from typing_extensions import Self

from sympy import Matrix as SympyMatrix, MatrixSymbol, MatrixExpr
from sympy.physics.vector import vlatex

from mathpad.core.val import DimensionError, Dimensionless, Val, Q, SumDimensionsMismatchError
from mathpad.core.frame import Frame
from mathpad.core.vector_space import VectorSpace, VectorSpaceT
from mathpad.core.vector import Vector

if TYPE_CHECKING:
    from mathpad.core.equation import Equation


L = TypeVar("L", bound=VectorSpace) # type: ignore [reportMissingTypeArgument]
R = TypeVar("R", bound=VectorSpace) # type: ignore [reportMissingTypeArgument]

class Matrix(Generic[L, R]):

    def __init__(
        self,
        expr: Union[str, Sequence[Sequence[Q[Val]]], SympyMatrix],
        *,
        type: Tuple[Frame[L], Frame[R]],
        check_val_dims: bool = True
    ):
        left_frame, right_frame = type
        self.left_frame = left_frame
        self.right_frame = right_frame


        if isinstance(expr, (SympyMatrix, MatrixExpr)):
            self.expr = expr
        
        elif isinstance(expr, str):
            assert expr[0].isupper(), \
                "Matrix names must start with an uppercase letter"

            sym = "\\mathbf{" + expr + "}"
            
            self.expr = MatrixSymbol(sym, len(left_frame.space.base_units), len(right_frame.space.base_units))
        
        else: # Sequence[Sequence[Q[Val]]
            
            assert len(expr) == len(left_frame), \
                f"Matrix must have the same number of rows as the left space. Instead got {len(expr)} (rows) != {len(left_frame)} (frame)"
            
            assert all(len(row) == len(right_frame) for row in expr), \
                f"Matrix must have the same number of columns as the right space. Instead got {len(expr[0])} (rows) != {len(right_frame)} (frame)"

            self_expr = []

            for i, (row, a_units) in enumerate(zip(expr, left_frame.space.base_units)):
                row_expr = []
                for j, (el, b_units) in enumerate(zip(row, right_frame.space.base_units)):
                    if isinstance(el, Val):
                        if check_val_dims:
                            expected_units = b_units / a_units
                            try:
                                DimensionError.check(expected_units, el)

                            except DimensionError as e:

                                def units2str(units: Val) -> str:
                                    return "dimensionless" if units.units == 1 else str(units.units)
                                    
                                raise DimensionError(
                                    f"Matrix element [{i}, {j}] has incorrect units.\n"
                                    f"Expected {units2str(expected_units)}, got {units2str(el)}.\n"
                                    f"If you are constructing a matrix from arithmetic between Vals and primitive numbers, "
                                    "consider passing check_val_dims=False to this constructor."
                                ) from e

                        row_expr.append(el.expr)
                    else:
                        row_expr.append(el)

                self_expr.append(row_expr)
            
            assert i + 1 == len(left_frame.space.base_units), \
                f"Matrix must have {len(left_frame.space.base_units)} rows, got {i + 1}"
            
            assert j + 1 == len(right_frame.space.base_units), \
                f"Matrix must have {len(right_frame.space.base_units)} columns, got {j + 1}"

            self.expr = SympyMatrix(self_expr)
    
    def __mul__(self, other: Q[Val]) -> 'Matrix[L, Any]':
        "Matrix[L, R] * Q[Val] => Matrix[L, Unknown]"

        assert not isinstance(other, (Matrix, Vector)), \
            "The '*' operator is only supported for scalars. Use '@' for matrix&vector multiplication instead."

        if not isinstance(other, Val):
            other = Dimensionless(1, other)

        return Matrix(
            self.expr * other.expr,
            type=(
                self.left_frame,
                self.right_frame * other,
            )
        )
    
    def _repr(self, _with_units: bool) -> str:
        return repr(self)


    def __rmul__(self, other: Q[Val]) -> 'Matrix[L, Any]':
        "Q[Val] * Matrix[L, R] => Matrix[L, R]"

        assert not isinstance(other, (Matrix, Vector)), \
            "The '*' operator is only supported for scalars. Use '@' for matrix&vector multiplication instead."

        if not isinstance(other, Val):
            other = Dimensionless(1, other)

        return Matrix(
            self.expr * other.expr,
            type=(
                self.left_frame,
                self.right_frame * other,
            )
        )


    def __add__(self, other: Self) -> Self:
        "Matrix[L, R] + Matrix[L, R] => Matrix[L, R]"
        assert other.left_frame is self.left_frame, \
            f"Matrix addition requires the same input space. {other.left_frame} is not equal to {self.left_frame}"
        assert other.right_frame is self.right_frame, \
            f"Matrix addition requires the same output space. {other.right_frame} is not equal to {self.right_frame}"

        return Matrix(
            self.expr + other.expr,
            type=(
                self.left_frame,
                self.right_frame
            )
        )

    
    def __sub__(self, other: Self) -> Self:
        "Matrix[L, R] - Matrix[L, R] => Matrix[L, R]"
        assert other.left_frame is self.left_frame, \
            f"Matrix addition requires the same input space. {other.left_frame} is not equal to {self.left_frame}"
        assert other.right_frame is self.right_frame, \
            f"Matrix addition requires the same output space. {other.right_frame} is not equal to {self.right_frame}"


        return Matrix(
            self.expr - other.expr,
            type=(
                self.left_frame,
                self.right_frame
            )
        )

        
    def __str__(self) -> str:
        return f"{self.expr} {self.right_frame} ⟷ {self.left_frame}"


    def _repr_latex_(self, wrapped: bool = True):

        # TODO: get vlatex() to display the MatrixSymbol as a \vec{} always
        # vlatex(self.expr) if isinstance(self.expr, MatrixSymbol) else
        
        # if isinstance(self.expr, Derivative):
        #     # workaround for vlatex() crashing on vector derivatives.
        #     orig_expr_variables = self.expr.__class__.variables
        #     self.expr.__class__.variables = self.expr._wrt_variables # type: ignore
        # else:
        #     orig_expr_variables = None

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
    
        # if orig_expr_variables:
        #     # undo temp monkeypatch
        #     self.expr.__class__.variables = orig_expr_variables # type: ignore



        left_vectorspace_ltx = self.left_frame._repr_latex_(wrapped=False)
        right_vectorspace_ltx = self.right_frame._repr_latex_(wrapped=False)
        
        def spacer(em: float) -> str:
            return "\\hspace{%sem}" % em

        full_ltx = f"{expr_ltx} {spacer(1.25)} {left_vectorspace_ltx} {spacer(0.75)} ⟷ {spacer(0.75)} {right_vectorspace_ltx}"

        return f"$$ {full_ltx} $$" if wrapped else full_ltx

    @overload
    def __matmul__(self, other: Vector[R]) -> Vector[L]:
        "Matrix[L, R] @ Vec[R] => Vec[L]"
        ...
    
    @overload
    def __matmul__(self, other: 'Matrix[R, VectorSpaceT]') -> 'Matrix[L, VectorSpaceT]':
        "Matrix[L, R] @ Matrix[R, T] => Matrix[L, T]"
        ...
    
    def __matmul__(self, other: Union[Vector[R], 'Matrix[R, VectorSpaceT]']) -> Union[Vector[L], 'Matrix[L, VectorSpaceT]']:
        if isinstance(other, Vector):
            # Matrix[L, R] @ Vec[R] => Vec[L]

            assert other.frame == self.right_frame, \
                "Vector-Matrix multiplication must take the form `Matrix[L, R] @ Vec[R] => Vec[L]`" \
                f"Matrix expects {self.right_frame}, Vector has {other.frame}"

            return Vector(self.left_frame, self.expr @ other.expr)
        
        elif isinstance(other, Matrix):
            # Matrix[L, R] @ Matrix[R, T] => Matrix[L, T]
            assert other.left_frame == self.right_frame, \
                "Matrix-Matrix multiplication (composition) must take the form `Matrix[L, R] @ Matrix[R, A] => Matrix[L, A]`" \
                f"Left Matrix expects {self.right_frame}, Right Matrix has {other.left_frame}"

            return Matrix(self.expr @ other.expr, type=(self.left_frame, other.right_frame))
        
        else:
            raise TypeError(f"Cannot multiply matrix by {type(other)}")
    
    def __rmatmul__(
        self,
        other: Vector[L]
    ) -> Vector[R]:
        "Vec[L] @ Matrix[L, R] => Vec[R]"

        assert self.left_frame == other.frame, \
            "Vector-Matrix multiplication (projection) must take the form `Vec[L] @ Matrix[L, R] => Vec[R]`" \
            f"Matrix expects {self.left_frame}, Vector has {other.frame}"

        return Vector(self.right_frame, other.expr.T @ self.expr)
    
    def __getitem__(self, key: Tuple[int, int]) -> Val:
        "Matrix[i, j] => Val"
        i, j = key
        units = self.right_frame.space.base_units[j] / self.left_frame.space.base_units[i]
        return Val(units.units, self.expr[i, j]) # type: ignore

    @property
    def T(self):
        "Get the transpose of the matrix"
        return Matrix(
            self.expr.transpose(),
            type=(
                self.right_frame,
                self.left_frame
            )
        )
    
    @property
    def inv(self) -> Self:
        "Inverse of a matrix"
        return Matrix(
            self.expr.inv(),
            type=(
                self.left_frame,
                self.right_frame
            )
        )
    
    
    def __eq__(self, other: Self) -> "Equation[Self]":
        from mathpad.core.equation import Equation
        
        for a, b in zip(self.left_frame.space.base_units, other.left_frame.space.base_units):
            SumDimensionsMismatchError.check(a, "==", b) # type: ignore
            
        for a, b in zip(self.right_frame.space.base_units, other.right_frame.space.base_units):
            SumDimensionsMismatchError.check(a, "==", b) # type: ignore

        return Equation(self, other)


    def __iter__(self) -> Iterator[List[Val]]:
        rows, cols = len(self.left_frame), len(self.right_frame)
        return (
            [self[i, j] for j in range(cols)]
            for i in range(rows)
        )


class VectorSpaceMapping(Generic[L, R]):
    def __init__(self, type: Tuple[L, R]):
        self.type = type
    
    def __call__(self, *exprs: Union[str, Sequence[Q[Val]]], check: bool = True) -> Matrix[L, R]:
        try:
            name, = exprs
            assert isinstance(name, str)
            return Matrix(name, type=self.type, check_val_dims=check)
        except (TypeError, ValueError, AssertionError):
            return Matrix([*[*exprs]], type=self.type, check_val_dims=check)

    @property
    def I(self) -> Matrix[L, R]:
        "Get the identity matrix for this VectorSpaceMapping"

        left_frame, right_frame = self.type
        assert len(left_frame) == len(right_frame), \
            "Identity matrix must have equal length input and output spaces"

        return Matrix(SympyMatrix.eye(len(left_frame)), type=self.type) # type: ignore

class _MatrixConstructor:
    def __getitem__(self, type: Tuple[Frame[L], Frame[R]]) -> VectorSpaceMapping[L, R]:
        return VectorSpaceMapping(type)

        
Mat = _MatrixConstructor()