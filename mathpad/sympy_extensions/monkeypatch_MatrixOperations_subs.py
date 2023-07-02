
from sympy.matrices.common import MatrixOperations
from sympy.core.expr import Expr

from .monkeypatch import monkeypatch_method

@monkeypatch_method(MatrixOperations)
def subs(self: MatrixOperations, *args: Expr) -> Expr:  # should mirror core.basic.subs
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

    if len(args) == 2:
        val, new_val = args
        if self is val:
            return new_val
        
    subs_map, = args

    # otherwise apply subs to each element
    return self.applyfunc(lambda x: x.subs(subs_map)) # type: ignore
