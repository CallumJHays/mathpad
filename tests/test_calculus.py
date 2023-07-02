
from mathpad import *

def test_diff():
    a = 10 * meters
    b = "b" * meters
    x = a + b
    assert diff(x) == 0 * meters / second
    assert diff(x, 2) == 0 * meters / second ** 2
    assert diff(x, wrt=b) == 1

def test_diff_negative_order_fails():
    a = 10 * meters
    b = "b" * meters
    x = a + b
    try:
        diff(x, -1)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"

def test_diff_wrt_nonsymbol_fails():
    try:
        diff(
            15 * m / s**2,
            wrt=1 * meter
        )
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"

def test_R3_diff():
    O = R3("O")
    t = "t" * s
    vec = O[
        t,
        2 * t**-1,
        3 * t**2
    ]
    expected = (O / s)[1, -2/t**2, 6*t]
    actual = diff(vec)

    assert (actual == expected).eval()

def test_integral():
    a = 10 * meters
    b = "b" * meters
    x = a + b
    assert integral(x) == 5 * meters * seconds
    assert integral(integral(x)) == 0.5 * t**2 * (b + 10)
    assert integral(x, wrt=b) == 5 * b ** 2 / 2

def test_integral_wrt_nonsymbol_fails():
    try:
        integral(
            15 * m / s**2,
            wrt=1 * meter
        )
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"

def test_R3_integral():
    O = R3("O")
    t = "t" * s
    vec = O[
        t,
        2 * t**-1,
        3 * t**2
    ]
    expected = (O * s)[
        t**2 / 2,
        2 * log(t),
        t**3,
    ]
    actual = integral(vec)

    assert (actual == expected).eval()