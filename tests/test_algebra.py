from mathpad import *

def test_sym_subs():
    x = "x" * m
    y = "y" * m
    z = "z" * m
    vec = x + 2 * y + 3 * z

    eqn = subs(vec, {x: 1, y: 2, z: 3}) == 14
    assert eqn.eval()

def test_R3_sym_subs():
    O = R3("O") * m
    x = "x" * m
    y = "y" * m
    z = "z" * m
    vec = O[x, y, z]
    vec2 = O[1, 2, 3]
    x2, y2, z2 = vec2

    eqn = subs(vec, {x: x2, y: y2, z: z2}) == vec2
    assert eqn.eval()

def test_sym_factor():
    x = "x" * dimensionless
    eqn = factor(x**3 - x**2 + x - 1) == (x - 1) * (x**2 + 1)
    assert eqn.eval()

def test_R3_sym_simplify():
    O = R3("O")
    x = "x" * m
    y = "y" * m
    z = "z" * m
    vec = O[x, y, z]

    eqn = simplify(vec) == vec
    assert eqn.eval()