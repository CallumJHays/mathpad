from mathpad import *

import sympy

def test_sqrt():
    x = 4 * m
    y = sqrt(x)

    assert y.units == (m ** 0.5).units
    assert y.expr == 2
    assert str(y) == "2 meters**0.5"

def test_sqrt_sym():
    x = "x" * m ** 0.5
    y = sqrt(x)

    assert y.units == (m ** 0.25).units
    assert y.expr == sympy.sqrt(x.expr)
    assert str(y) == "x**0.5 meters**0.25"
