

from typing import Generic, Sequence, Tuple, TypeVar, Union, overload
from typing_extensions import Self

from sympy import Matrix as SympyMatrix, MatrixSymbol, MatrixExpr
from sympy.physics.vector import vlatex

from mathpad.val import DimensionError, Dimensionless, Val, Q
from mathpad.vector_space import VectorSpace, VectorSpaceT as T
from mathpad.vector import Vector


L = TypeVar("L", bound=VectorSpace)
R = TypeVar("R", bound=VectorSpace)

class Matrix(Generic[L, R]):

    @classmethod
    def identity(
        cls,
        left_space: L,
        right_space: R
    ) -> 'Matrix[L, R]':
        "Identity matrix of a given space"

        size = len(left_space)

        if right_space:
            assert len(right_space) == size, \
                "Identity matrix must have equal length input and output spaces"

        return cls(left_space, right_space, SympyMatrix.eye(size)) # type: ignore

    def __init__(
        self,
        left_space: L,
        right_space: R,
        expr: Union[str, Sequence[Sequence[Q[Val]]], SympyMatrix],
        *,
        check_val_dims: bool = True
    ):
        self.left_space = left_space
        self.right_space = right_space


        if isinstance(expr, (SympyMatrix, MatrixExpr)):
            self.expr = expr
        
        elif isinstance(expr, str):
            assert expr[0].isupper(), \
                "Matrix names must start with an uppercase letter"

            sym = "\\mathbf{" + expr + "}"
            
            self.expr = MatrixSymbol(sym, len(left_space.base_units), len(right_space.base_units))
        
        else:
            assert len(expr) == len(left_space), \
                "Matrix must have the same number of rows as the left space"
            
            assert all(len(row) == len(right_space) for row in expr), \
                "Matrix must have the same number of columns as the right space"

            self_expr = []

            for i, (row, a_units) in enumerate(zip(expr, left_space.base_units)):
                row_expr = []
                for j, (el, b_units) in enumerate(zip(row, right_space.base_units)):
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
            
            assert i + 1 == len(left_space.base_units), \
                f"Matrix must have {len(left_space.base_units)} rows, got {i + 1}"
            
            assert j + 1 == len(right_space.base_units), \
                f"Matrix must have {len(right_space.base_units)} columns, got {j + 1}"

            self.expr = SympyMatrix(self_expr)
    
    def __mul__(self, other: Q[Val]) -> 'Matrix[L, VectorSpace]':
        "Self[L, R] * Q[Val] => Self[L, Unknown]"

        assert not isinstance(other, (Matrix, Vector)), \
            "The '*' operator is only supported for scalars. Use '@' for matrix&vector multiplication instead."

        if not isinstance(other, Val):
            other = Dimensionless(1, other)

        return Matrix(
            self.left_space,
            self.right_space * other,
            self.expr * other.expr
        )


    def __rmul__(self, other: Q[Val]) -> 'Matrix[L, VectorSpace]':
        "Q[Val] * Self[L, R] => Self[L, R]"

        assert not isinstance(other, (Matrix, Vector)), \
            "The '*' operator is only supported for scalars. Use '@' for matrix&vector multiplication instead."

        if not isinstance(other, Val):
            other = Dimensionless(1, other)

        return Matrix(
            self.left_space,
            self.right_space * other,
            self.expr * other.expr
        )


    def __add__(self, other: Self) -> Self:
        "Self[L, R] + Self[L, R] => Self[L, R]"
        assert other.left_space == self.left_space, \
            "Matrix addition requires the same input space"

        return Matrix(self.left_space, self.right_space, self.expr + other.expr) # type: ignore
    

    def inv(self) -> Self:
        "Inverse of a matrix"
        return Matrix(self.right_space, self.left_space, self.expr.inv()) # type: ignore

    
    def __sub__(self, other: Self) -> Self:
        "Self[L, R] - Self[L, R] => Self[L, R]"
        assert other.left_space == self.left_space, \
            "Matrix addition requires the same input space"

        return Matrix(self.left_space, self.right_space, self.expr - other.expr) # type: ignore

        
    def __str__(self) -> str:
        return f"{self.expr} {self.right_space} ⟷ {self.left_space}"


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



        left_vectorspace_ltx = self.left_space._repr_latex_(wrapped=False)
        right_vectorspace_ltx = self.right_space._repr_latex_(wrapped=False)
        
        def spacer(em: float) -> str:
            return "\\hspace{%sem}" % em

        full_ltx = f"{expr_ltx} {spacer(1.25)} {left_vectorspace_ltx} {spacer(0.75)} ⟷ {spacer(0.75)} {right_vectorspace_ltx}"

        return f"$$ {full_ltx} $$" if wrapped else full_ltx

    @overload
    def __matmul__(self, other: Vector[R]) -> Vector[L]:
        "Self[L, R] @ Vec[R] => Vec[L]"
        ...
    
    @overload
    def __matmul__(self, other: 'Matrix[R, T]') -> 'Matrix[L, T]':
        "Self[L, R] @ Matrix[R, T] => Matrix[L, T]"
        ...
    
    def __matmul__(self, other: Union[Vector[R], 'Matrix[R, T]']) -> Union[Vector[L], 'Matrix[L, T]']:
        if isinstance(other, Vector):
            # Self[L, R] @ Vec[R] => Vec[L]

            assert other.space == self.right_space, \
                "Vector-Matrix multiplication must take the form `Self[L, R] @ Vec[R] => Vec[L]`" \
                f"Matrix expects {self.right_space}, Vector has {other.space}"

            return Vector(self.left_space, self.expr @ other.expr)
        
        elif isinstance(other, Matrix):
            # Self[L, R] @ Matrix[R, T] => Matrix[L, T]
            assert other.left_space == self.right_space, \
                "Matrix-Matrix multiplication must take the form `Self[L, R] @ Matrix[R, A] => Matrix[L, A]`" \
                f"Left Matrix expects {self.right_space}, Right Matrix has {other.left_space}"

            return Matrix(self.left_space, other.right_space, self.expr @ other.expr)
        
        else:
            raise TypeError(f"Cannot multiply matrix by {type(other)}")
    
    def __rmatmul__(
        self,
        other: Vector[L]
    ) -> Vector[R]:
        "Vec[L] @ Self[L, R] => Vec[R]"

        assert other.space == self.left_space, \
            "Vector-Matrix multiplication must take the form `Vec[L] @ Self[L, R] => Vec[R]`" \
            f"Matrix expects {self.left_space}, Vector has {other.space}"

        return Vector(self.right_space, other.expr.T @ self.expr)
    
    def __getitem__(self, key: Tuple[int, int]) -> Val:
        "Self[i, j] => Val"
        i, j = key
        units = self.right_space.base_units[j] / self.left_space.base_units[i]
        return Val(units.units, self.expr[i, j]) # type: ignore