import sympy
from sympy.physics.vector.printing import VectorLatexPrinter

from .monkeypatch import monkeypatch_method

@monkeypatch_method(VectorLatexPrinter)
def _print_Derivative(self: VectorLatexPrinter, der_expr: sympy.Expr) -> str:
    "same as the original but der_expr.doit() is not called"
    from sympy.physics.vector.functions import dynamicsymbols
    from sympy import Derivative
    from sympy.core.function import AppliedUndef
    
    # make sure it is in the right form
    ## der_expr = der_expr.doit() <-- removed
    if not isinstance(der_expr, Derivative):
        return r"\left(%s\right)" % self.doprint(der_expr)

    # check if expr is a dynamicsymbol
    t = dynamicsymbols._t
    expr = der_expr.expr
    red = expr.atoms(AppliedUndef)
    syms = der_expr.variables
    test1 = not all(True for i in red if i.free_symbols == {t})
    test2 = not all(t == i for i in syms)
    if test1 or test2:
        return super()._print_Derivative(der_expr)

    # done checking
    dots = len(syms)

    base = str(expr)[:-3]


    ## HERE IS THE SECOND CHANGE: skip all the rest and return base
    # base_split = base.split('_', 1)
    # base = base_split[0]
    [sym] = syms
    if sym == t: # if 1st or 2nd order time derivative, use dot notation
        if dots == 1:
            return r"\dot{%s}" % base # dots imply time derivative
        elif dots == 2:
            return r"\ddot{%s}" % base
    
    return (
        r"\frac{d^{%d}}{d%s^{%d}} %s" % (dots, base, dots, self.doprint(sym))
    )
