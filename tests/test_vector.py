from mathpad import *

from _test_utils import expect_err

def test_R3_disp():
    O = R3("O")
    vec = O[1, 2, 3]

    assert str(vec) == "[1, 2, 3] wrt. O"

def test_R3_disp_sym():
    O = R3("O") * m
    vec = "vec" @ O

    assert str(vec) == r'vec{vec} wrt. O'

def test_R3_add_R3():
    O = R3("O")
    vec = O[1, 2, 3]
    vec2 = O[4, 5, 6]

    eqn = vec + vec2 == O[5, 7, 9]
    assert eqn.eval()

def test_R3_add_R2_fails():
    vec = R3("O3")[1, 2, 3]
    vec2 = R2("O2")[4, 5]

    with expect_err(AssertionError):
        vec + vec2 # type: ignore

    with expect_err(AssertionError):
        vec2 + vec # type: ignore

def test_R3_add_Val_fails():
    O = R3("O")
    vec = O[1, 2, 3]
    val = 1 * meter

    with expect_err(AssertionError):
        vec + val # type: ignore
        
    with expect_err(AssertionError):
        val + vec # type: ignore


def test_R3_sub_R3():
    O = R3("O")
    vec = O[1, 2, 3]
    vec2 = O[4, 5, 6]

    eqn = vec - vec2 == O[-3, -3, -3]
    assert eqn.eval()

def test_R3_sub_R2_fails():
    vec = R3("O3")[1, 2, 3]
    vec2 = R2("O2")[4, 5]

    with expect_err(AssertionError):
        vec - vec2 # type: ignore

    with expect_err(AssertionError):
        vec2 - vec # type: ignore

def test_R3_mul_Val():
    O = R3("O")
    vec = O[1, 2, 3]
    val = 2 * meter

    eqn = vec * val == O[2, 4, 6] * meter
    assert eqn.eval()

def test_R3_div_Val():
    O = R3("O")
    vec = O[1, 2, 3]
    val = 2 * meter

    eqn = vec / val == O[0.5, 1, 1.5] / meter
    assert eqn.eval()

def test_Val_div_R3_fails():
    O = R3("O")
    vec = O[1, 2, 3]

    with expect_err(AssertionError):
        2 * meter / vec # type: ignore
        
    with expect_err(AssertionError):
        2 / vec # type: ignore

def test_R3_cross():
    O = R3("O") * m
    vec = O[1, 2, 3]
    vec2 = O[4, 5, 6]

    eqn = vec.cross(vec2) == O[-3, 6, -3] * meter
    assert eqn.eval()


def test_R2_cross_fails():
    O = R2("O") * m
    vec = O[1, 2]
    vec2 = O[3, 4]

    with expect_err(AssertionError):
        vec.cross(vec2)

def test_R3_dot():
    O = R3("O") * m
    vec = O[1, 2, 3]
    vec2 = O[4, 5, 6]

    eqn = vec.dot(vec2) == 32 * meter**2
    assert eqn.eval()  

def test_R3_sym_dot():
    O = R3("O") * m
    vec = "vec" @ O
    vec2 = O[1, 2, 3]
    
    x1, y1, z1 = vec
    x2, y2, z2 = vec2

    eqn = vec.dot(vec2) == x1 * x2 + y1 * y2 + z1 * z2
    assert eqn.eval()

def test_R3_sym_add():
    O = R3("O") * m
    vec = "vec" @ O
    vec2 = O[1, 2, 3]

    # TODO: get matrix expressions printing better as str()
    # assert str(res) == 'O["vec"] + O[1, 2, 3]'

    eqn = vec + vec2 == O[
        1 + vec.i,
        2 + vec.j,
        3 + vec.k
    ]
    assert eqn.eval()

def test_R3_sym_cross():
    O = R3("O") * m
    vec = "vec" @ O
    vec2 = O[1, 2, 3]

    eqn = vec.cross(vec2) == O[
        3 * vec.j - 2 * vec.k,
        -3 * vec.i + vec.k,
        2 * vec.i - vec.j
    ] * m # 
    assert eqn.eval()

def test_R3_diff_basic():
    O = R3("O") * m
    vec = O[0, 0, 0]
    dvec = diff(vec)

    eqn = dvec == vec / s
    assert eqn.eval()

def test_R3_diff_syms():
    O = R3("O") * m
    x = "x(t)" * m
    y = "y(t)" * m
    z = "z(t)" * m
    vec = O[x, y, z]

    dvec = diff(vec)
    out_frame = O / s
    assert out_frame.space == dvec.frame.space

    eqn = dvec == out_frame[
        diff(x),
        diff(y),
        diff(z)
    ]
    assert eqn.eval()

def test_R3_integral_basic():
    O = R3("O") * m
    vec = O[1, 2, 3]
    ivec = integral(vec)

    eqn = ivec == vec * t
    assert eqn.eval()

def test_R3_integral_syms():
    O = R3("O") * m
    x = "x(t)" * m
    y = "y(t)" * m
    z = "z(t)" * m
    vec = O[x, y, z]

    ivec = integral(vec)

    eqn = ivec == (O * s)[
        integral(x),
        integral(y),
        integral(z)
    ]
    assert eqn.eval()

def test_R3_sym_func():
    O = R3("O") * m
    vec = "vec(t)" @ O

def test_R3_sym_func_repr_latex():
    O = R3("O") * m
    vec = "vec(t)" @ O

    expected = r"$$ \vec{vec}(t) \hspace{1.25em} \begin{matrix} \hat{i} \cdot \text{m} \\ \hat{j} \cdot \text{m} \\ \hat{k} \cdot \text{m} \end{matrix}\normalsize \hspace{0.7em} \small\text{wrt. O}\normalsize $$"

    assert vec._repr_latex_() == expected


def test_R3_sym_func_diff():
    O = R3("O") * m
    vec = "vec(t)" @ O

    dvec = diff(vec)
    assert dvec.frame == O / s


def test_R3_sym_func_diff_repr_latex():
    O = R3("O") * m
    vec = "vec(t)" @ O

    dvec = diff(vec)
    
    expected = r"$$ \dot{\vec{vec}} \hspace{1.25em} \begin{matrix} \hat{i} \cdot \frac{\text{m}}{\text{s}} \\ \hat{j} \cdot \frac{\text{m}}{\text{s}} \\ \hat{k} \cdot \frac{\text{m}}{\text{s}} \end{matrix}\normalsize \hspace{0.7em} \small\text{wrt. O}\normalsize $$"

    assert dvec._repr_latex_() == expected


def test_R3_sym_func_diff_iter():
    O = R3("O") * m
    vec = "vec(t)" @ O
    
    x, y, z = diff(vec)

    assert str(x) == 'Derivative(\\vec{vec}_{i}(t), t) meters/second'
    assert str(y) == 'Derivative(\\vec{vec}_{j}(t), t) meters/second'
    assert str(z) == 'Derivative(\\vec{vec}_{k}(t), t) meters/second'