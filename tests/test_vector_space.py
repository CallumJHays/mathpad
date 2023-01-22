from mathpad import *

from _test_utils import expect_err

def test_R3_anonymous():
    vec = R3()[1, 2, 3]

    assert str(vec) == "[1, 2, 3]"

def test_R3_basis_constructors():
    O = R3("O")

    assert O.i == O[1, 0, 0]
    assert O.j == O[0, 1, 0]
    assert O.k == O[0, 0, 1]

def test_VectorSpace_constructor():
    O = R3("O")
    vec = O[1, 2, 3]

    assert vec.space is O
    assert vec == O[1, 2, 3]
    assert vec.i == 1
    assert vec.j == 2
    assert vec.k == 3

def test_VectorSpace_abstract_only():
    with expect_err(AssertionError):
        VectorSpace("O")

def test_R3_disp():
    O = R3("O")
    
    assert str(O) == '<R3 name="O">'
    assert str(R3()) == '<R3>'


def test_must_specify_base_units():
    with expect_err(AssertionError):
        class MyVecSpace(VectorSpace[Length]):
            base_names = "i",

def test_must_specify_base_names():
    with expect_err(AssertionError):
        class MyVecSpace(VectorSpace[Length]):
            base_units = meter,

def test_must_specify_base_both():
    with expect_err(AssertionError):
        class MyVecSpace(VectorSpace):
            pass

def test_base_names_must_match_base_units():
    with expect_err(AssertionError):
        class MyVecSpace(VectorSpace):
            base_units = meter, meter # type: ignore
            base_names = "i",

def test_custom_VectorSpace():
    
    class CustomVectorSpace(
        # commonly referred to as "state space" - you can put any units you want
        VectorSpace[Energy, Force, Angle, AngularVelocity]
    ):
        base_units = coulomb, newton, radian, radian / second # type: ignore
        base_names = "charge", "input", "theta", "omega"
    
    State = CustomVectorSpace("State")
    eqn = State.charge == State[1, 0, 0, 0]
    assert eqn.eval()
    eqn = State.input == State[0, 1, 0, 0]
    assert eqn.eval()
    eqn = State.theta == State[0, 0, 1, 0]
    assert eqn.eval()
    eqn = State.omega == State[0, 0, 0, 1]
    assert eqn.eval()

    state = State[1, 2, 3, 4]

    assert state.charge == 1 * coulomb
    assert state.input == 2 * newton
    assert state.theta == 3 * radian
    assert state.omega == 4 * radian / second

def test_VectorSpace_div_Val():
    O = R3("O")

    for units in (O / m).base_units:
        assert units == 1

def test_Val_div_VectorSpace():
    O = R3("O")

    for units in (m / O).base_units:
        assert units == 1

def test_VectorSpace_mul_Val():
    O = R3("O")

    for units in (O * m).base_units:
        assert units == m**2

def test_Val_mul_VectorSpace():
    O = R3("O")

    for units in (m * O).base_units:
        assert units == m**2

def test_create_vector_function():
    x = "x" * m
    s = "s(x)" @ R3("O")
    v = diff(s, wrt=x)
    print(v)
