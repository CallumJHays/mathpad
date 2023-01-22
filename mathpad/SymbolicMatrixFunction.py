from typing import Any, Collection, Dict, Sequence
from sympy import Expr, MatrixExpr, Basic, MatrixSymbol, sin, Matrix, Tuple, Function, solve, ImmutableDenseMatrix, Symbol, symbols, StrPrinter, Eq, randMatrix, cos, MatMul, Derivative, Integral
from sympy.core import cacheit
from sympy.core.function import UndefinedFunction
from sympy.printing.latex import LatexPrinter
from sympy.core.sympify import _sympify
from sympy.core.symbol import Str
from sympy.multipledispatch import dispatch
from sympy.utilities.iterables import is_sequence
import unittest
 

__all__ = ["SymbolicMatrixFunction", "solve_with_sym_matrices"]


class SymbolicMatrixFunction(MatrixSymbol):

    def __new__(cls, name: "Str | str", n: int, m: int, function_of: Sequence[Expr]):
        n, m = _sympify(n), _sympify(m)

        cls._check_dim(m)
        cls._check_dim(n)

        if isinstance(name, str):
            name = Str(name)

        obj = Basic.__new__(cls, name, n, m, Tuple(*function_of))
        return obj


    def __init__(self, _name: str, _n: int, _m: int, function_of: Sequence[Expr]):
        assert any(function_of), "SymbolicMatrixFunction must be a function of at least 1 expression"
        self.function_of: Tuple = Tuple(*function_of) # store as immutable tuple so we stay hashable
    

    def _sympystr(self, printer: StrPrinter) -> str:
        return f"{printer.doprint(self.name)}({', '.join(printer.doprint(x) for x in self.function_of)})"
    

    def _latex(self, printer: LatexPrinter):
        return f"{printer.doprint(self.name)}({', '.join(printer.doprint(x) for x in self.function_of)})"
    

    @property
    def free_symbols(self):
        return set(
            sym
            for x in self.function_of
            for sym in x.free_symbols
        )
        

    def diff(self, *args, **kwargs):
        return Derivative(self, *args, **kwargs)


    def _entry(self, i, j) -> Function:
        "Return a function instead of a symbol"
        return Function(f"{self.name}[{i}, {j}]")(*self.function_of) # type: ignore


    def integrate(self, *wrt: Symbol, **kwargs):
        return Integral(self, *wrt, **kwargs)
    

    def __matmul__(self, other):
        if other == 1: # TODO: Identity mat as well?
            return self
        return MatMul(self, other)
        
    def __rmatmul__(self, other):
        if other == 1: # TODO: Identity mat as well?
            return self
        return MatMul(other, self)
    
    def __mul__(self, other):
        if other == 1: # TODO: Identity mat as well?
            return self
        return MatMul(self, other)
        
    def __rmul__(self, other):
        if other == 1: # TODO: Identity mat as well?
            return self
        return MatMul(other, self)

        
    def _eval_subs(self, old, new):
        """Override this stub if you want to do anything more than
        attempt a replacement of old with new in the arguments of self.

        See also
        ========

        _subs
        """
        return None
    
    # @cacheit
    # def has(self, *patterns):
    #     # reqd for integral impl
    #     return super().has(*patterns) or all(p in self.function_of for p in patterns)

from sympy.matrices.common import MatrixOperations
def monkeypatch_MatrixOperations_subs(self: MatrixOperations, *args: Expr):  # should mirror core.basic.subs
    # Monkey-patched MatrixOperations.subs implemenation to short-circuit out if self is in subs_map.
    """
    Return a new matrix with subs applied to each entry.

    Examples
    ========

    >>> from sympy.abc import x, y
    >>> from sympy import SparseMatrix, Matrix
    >>> SparseMatrix(1, 1, [x])
    Matrix([[x]])
    >>> _.subs(x, y)
    Matrix([[y]])
    >>> Matrix(_).subs(y, x)
    Matrix([[x]])
    """

    subs_map = {
        args[0]: args[1]
    } if len(args) == 2 else args[0]

    # first check if we are substituting the whole matrix:
    if self in subs_map:
        return subs_map[self]

    # otherwise apply subs to each element
    return self.applyfunc(lambda x: x.subs(subs_map))

setattr(MatrixOperations, "subs", monkeypatch_MatrixOperations_subs)


@dispatch(MatrixExpr, Function) 
def _eval_is_eq(lhs: MatrixExpr, rhs: Function): # noqa:F811
    "This is required to prevent a bug with Eq() being evaluated during substitution" # TODO: comment
    if rhs.is_commutative: # type: ignore
        return False
    else:
        return None


@dispatch(SymbolicMatrixFunction, Function) 
def _eval_is_eq(lhs: SymbolicMatrixFunction, rhs: Function): # noqa:F811
    "This is required to prevent a bug with Eq() being evaluated during substitution" # TODO: comment
    if rhs.is_commutative or lhs.free_symbols != rhs.free_symbols:
        return False
    else:
        return None


def solve_with_sym_matrices(equations: Collection[Eq], *solve_for: Expr, explicit: bool = True):
    """
    solve() does not yet handle MatrixSymbol's properly. This function (kinda) does.
    Works by substituting each MatrixExpr with its ._as_explicit() version if `explicit`,
    otherwise a non-commutative symbol will be used in its place.

    PS:
    Setting explicit = False may speed up solving at the cost of not being able to solve problems wherein matrix internals are referenced in intermediary steps.
    This is just my current understanding as an engineering bachelor, so it may not be correct.
    """

    # populated in subbed_eqns()
    subs_map: Dict[MatrixSymbol, "Symbol | ImmutableDenseMatrix"] = {}

    for eqn in equations:
        # add matrices to subs_map
        for mat in eqn.atoms(MatrixSymbol if explicit else MatrixExpr):
            if mat not in subs_map:
                subs_map[mat] = mat.as_explicit() if explicit \
                    else Function(f"X{len(subs_map)}", commutative=False)(*mat.function_of) if isinstance(mat, SymbolicMatrixFunction) \
                    else Function(f"X{len(subs_map)}", commutative=False)(*mat.free_symbols) if mat.free_symbols \
                    else Symbol(f"X{len(subs_map)}", commutative=False)
                # subs_map[mat].is_Matrix = True

    # subbed_eqns = [
    #     Eq(eqn.lhs.subs(subs_map), eqn.rhs.subs(subs_map), evaluate=False)
    #     for eqn in equations
    # ]
    subbed_eqns = [eqn.subs(subs_map) for eqn in equations]
    sln = solve(subbed_eqns, *subs_map.values())
    
    # subbed_eqns2 = [
    #     Eq(eqn.lhs.subs(sln1), eqn.rhs.subs(sln1), evaluate=False)
    #     for eqn in subbed_eqns
    # ]
    # subbed_solve_for = [sym.subs(subs_map) for sym in solve_for]
    # sln2 = solve(subbed_eqns2, *subbed_solve_for)

    assert sln, "no solution found"

    res = tuple(sym.subs(subs_map).subs(sln).doit() for sym in solve_for)

    return res # TODO: support multiple solutions properly?




class TestSymbolicMatrixFunction(unittest.TestCase):

    def _assert_str_repr(self, x: Any, expected: str):
        self.assertEqual(str(x), expected)
        self.assertEqual(repr(x), expected)


    # def test_init(self):
    #     t = Symbol("t")
    #     SymbolicMatrixFunction("A", 3, 3, {t})
    
    
    # def test_repr(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     self._assert_str_repr(A, "A(t)")

    # def test_diff(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     dA = A.diff(t)
    #     self._assert_str_repr(dA, "Derivative(A(t), t)")


    # def test_integral(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     iA = A.integrate(t)
    #     self._assert_str_repr(iA, "Integral(A(t), t)")
    

    # def test_add(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     B = SymbolicMatrixFunction("B", 3, 3, {t})
    #     C = A + B
    #     self._assert_str_repr(C, "A(t) + B(t)")


    # def test_sub(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     B = SymbolicMatrixFunction("B", 3, 3, {t})
    #     C = A - B
    #     self._assert_str_repr(C, "A(t) - B(t)")
    

    # # def test_addsub_wrongshape_fails(self):
    # #     t = Symbol("t")
    # #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    # #     B = SymbolicMatrixFunction("B", 3, 2, {t})

    # #     with self.assertRaises(ShapeError):
    # #         A + B
    # #     with self.assertRaises(ShapeError):
    # #         A - B
    
    # def test_solve(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     B = randMatrix(3)
    #     slnB, = solve_with_sym_matrices([Eq(A, B)], A)
    #     assert slnB == B


    # def test_elements_are_functions(self):
    #     t = Symbol("t")
    #     A = SymbolicMatrixFunction("A", 3, 3, {t})
    #     x = A[1, 2]

    #     assert isinstance(x, Function)
    #     assert x.free_symbols == {t}
        
    #     self._assert_str_repr(x, "A[1, 2](t)")

    #     # should also work for as_explicit():
    #     y = A.as_explicit()[1, 2]
    #     assert isinstance(y, Function)
    #     assert y.free_symbols == {t}
    

    # def test_diff_multivariate(self):
    #     x, y, z = symbols("x,y,z") # type: ignore
    #     A = SymbolicMatrixFunction("A", 3, 3, [x, y, z])
    #     dA = A.diff(x, y)
    #     self._assert_str_repr(dA, "Derivative(A(x, y, z), x, y)")


    # def test_integral_multivariate(self):
    #     x, y, z = symbols("x,y,z") # type: ignore
    #     A = SymbolicMatrixFunction("A", 3, 3, [x, y, z])
    #     dA = A.integrate(x, y)
    #     self._assert_str_repr(dA, "Integral(A(x, y, z), x, y)")
    
    
    # def test_solve_2d_rotation_diff_undef_theta(self):
    #     t = Symbol("t")
    #     theta: Function = Function("theta")(t) # type: ignore
    #     R = SymbolicMatrixFunction("R", 2, 2, {theta})
    #     R_def_eqn: Eq = Eq(R, Matrix([
    #         [cos(theta), -sin(theta)], # type: ignore
    #         [sin(theta), cos(theta)]
    #     ]))

    #     sln_Rdiff_wrt_theta, sln_Rdiff_wrt_t = solve_with_sym_matrices(
    #         [R_def_eqn], R.diff(theta), R.diff(t)
    #     )
    #     sln_Rdiff_wrt_theta_expected = Matrix([
    #         [-sin(theta), -cos(theta)], # type: ignore
    #         [cos(theta), -sin(theta)] # type: ignore
    #     ])

    #     assert sln_Rdiff_wrt_theta == sln_Rdiff_wrt_theta_expected
    #     assert sln_Rdiff_wrt_t == theta.diff() * sln_Rdiff_wrt_theta_expected # chain rule


    # def test_solve_2d_rotation_diff_def_theta(self):
    #     t = Symbol("t")
    #     theta: Expr = t ** 2
    #     R = SymbolicMatrixFunction("R", 2, 2, [t])
    #     R_def_eqn: Eq = Eq(R, Matrix([
    #         [cos(theta), -sin(theta)], # type: ignore
    #         [sin(theta), cos(theta)]
    #     ]))

    #     sln_Rdiff, = solve_with_sym_matrices([R_def_eqn], R.diff(t))
    #     sln_Rdiff_wrt_theta_expected = theta.diff() * Matrix([ # chain rule
    #         [-sin(theta), -cos(theta)], # type: ignore
    #         [cos(theta), -sin(theta)] # type: ignore
    #     ])

    #     assert sln_Rdiff == sln_Rdiff_wrt_theta_expected

    def test_solve_2d_rotation_diff_undef_theta_nonexplicit(self):
        t = Symbol("t")
        theta: Function = Function("theta")(t) # type: ignore
        R = SymbolicMatrixFunction("R", 2, 2, {theta})
        R_def_eqn: Eq = Eq(R, Matrix([
            [cos(theta), -sin(theta)], # type: ignore
            [sin(theta), cos(theta)]
        ]), evaluate=False)

        sln_Rdiff_wrt_theta, sln_Rdiff_wrt_t = solve_with_sym_matrices(
            [R_def_eqn], R.diff(t),
            explicit=False
        )
        sln_Rdiff_wrt_theta_expected = Matrix([
            [-sin(theta), -cos(theta)], # type: ignore
            [cos(theta), -sin(theta)] # type: ignore
        ])

        assert sln_Rdiff_wrt_theta == sln_Rdiff_wrt_theta_expected
        assert sln_Rdiff_wrt_t == theta.diff() * sln_Rdiff_wrt_theta_expected # chain rule


    # def test_solve_2d_rotation_diff_def_theta_nonexplicit(self):
    #     t = Symbol("t")
    #     theta: Expr = t ** 2
    #     R = SymbolicMatrixFunction("R", 2, 2, {theta})
    #     R_def_eqn: Eq = Eq(R, Matrix([
    #         [cos(theta), -sin(theta)], # type: ignore
    #         [sin(theta), cos(theta)]
    #     ]))

    #     sln_Rdiff, = solve_with_sym_matrices([R_def_eqn], R.diff(t), explicit=False)
    #     sln_Rdiff_wrt_theta_expected = theta.diff() * Matrix([ # chain rule
    #         [-sin(theta), -cos(theta)], # type: ignore
    #         [cos(theta), -sin(theta)] # type: ignore
    #     ])

    #     assert sln_Rdiff == sln_Rdiff_wrt_theta_expected


if __name__ == "__main__":
    unittest.main()