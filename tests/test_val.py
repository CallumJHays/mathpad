from mathpad import *


def test_mul_meters_int():
    a = 10 * meters
    res = a * 5
    assert res.expr == 50
    assert res.units == meters.units


def test_mul_int_meters():
    a = 10 * meters
    res = 5 * a
    res = a * 5
    assert res.expr == 50
    assert res.units == meters.units


def test_mul_meters_seconds():
    a = 10 * meters
    b = 5 * seconds
    res = a * b
    assert res.expr == 50
    assert res.units == meter.units * second.units


def test_mul_meters_meters():
    a = 10 * meters
    b = 5 * meters
    res = a * b
    assert res.expr == 50
    assert res.units == meter.units * meter.units


def test_mul_meters_millimeters():
    a = 10 * meters
    b = 5 * millimeter
    res = a * b

    assert str(res) == "0.05 meters**2"


def test_mul_millimeters_meters():
    a = 10 * meters
    b = 5 * millimeters
    res = b * a

    assert str(res) == "0.05 meters**2"


def test_div_meters_int():
    a = 10 * meters
    res = a / 5

    assert str(res) == "2 meters"


def test_div_int_meters():
    a = 10 * meters
    res = 50 / a

    assert str(res) == "5 1/meters"


def test_div_meters_seconds():
    a = 10 * meters
    b = 5 * seconds
    res = a / b

    assert str(res) == "2 meters/second"


def test_div_meters_meters():
    a = 10 * meters
    b = 5 * meters
    res = a / b

    assert str(res) == "2"


def test_div_meters_centimeters():
    a = 10 * meters
    b = 5 * centimeters
    res = a / b

    assert str(res) == "200"


def test_div_centimeters_meters():
    a = 10 * meters
    b = 5 * centimeters
    res = b / a

    assert str(res) == "5e-3"


def test_add_meters_int():
    a = 10 * meters
    res = a + 5

    assert str(res) == "15 meters"


def test_add_int_meters():
    a = 10 * meters
    res = 50 + a

    assert str(res) == "60 meters"


def test_add_meters_seconds_fails():
    a = 10 * meters
    b = 5 * seconds
    try:
        a + b  # type: ignore
        assert False
    except SumDimensionsMismatch:
        assert True


def test_add_meters_meters():
    a = 10 * meters
    b = 5 * meters
    res = a + b

    assert str(res) == "15 meters"


def test_add_meters_kilometers():
    a = 10 * meters
    b = 5 * kilometers
    res = a + b

    assert str(res) == "5.01 kilometers"


def test_add_centimeters_meters():
    a = 100 * meters
    b = 5 * centimeters
    res = b + a

    assert str(res) == "100.05 meters"


def test_add_var_centimeters_var_meters():
    a = "a" * centimeters
    b = "b" * meters
    res = 100 * a + 5 * b

    assert str(res) == "a + 5*b meters"


def test_sub_meters_int():
    a = 10 * meters
    res = a - 5

    assert str(res) == "5 meters"


def test_sub_int_meters():
    a = 10 * meters
    res = 50 - a

    assert str(res) == "40 meters"


def test_sub_meters_seconds_fails():
    a = 10 * meters
    b = 5 * seconds
    try:
        a - b  # type: ignore
        assert False
    except SumDimensionsMismatch:
        assert True


def test_sub_meters_meters():
    a = 5 * meters
    b = 10 * meters
    res = a - b

    assert str(res) == "-5 meters"


def test_sub_meters_kilometers():
    a = 10 * meters
    b = 5 * kilometers
    res = a - b

    assert str(res) == "-4.99 kilometers"


def test_sub_centimeters_meters():
    a = 100 * meters
    b = 5 * centimeters
    res = b - a

    assert str(res) == "-99.95 meters"


def test_sub_var_centimeters_var_meters():
    a = "a" * centimeters
    b = "b" * meters
    res = 100 * a - 5 * b

    assert str(res) == "a - 5*b meters"


def test_pow_squared():
    a = "a" * meters
    res = a ** 2

    assert str(res) == "a**2 meters**2"


def test_pow_half():
    a = "a" * meters**2
    res = a ** 0.5

    assert str(res) == "a**0.5 meters"


def test_pow_neg_zero():
    a = "a" * meters
    res = a ** -0

    assert str(res) == "1"


def test_pow_neg_half():
    a = "a" * meters**2
    res = a ** -0.5

    assert str(res) == "a**(-0.5) meters**(-1.0)"


def test_rpow_100():
    a = "a" * dimensionless
    res = 100 ** a

    assert str(res) == "100**a"


def test_pow_100():
    a = "a" * meters
    res = a ** 100

    assert str(res) == "a**100 meters**100"


def test_pow_sym():
    a = "a" * meters
    b = "b" * dimensionless
    res = a ** b

    assert str(res) == "a**b meters**b"


# def test_pow_neg_sym():
#     a = "a" * meters
#     b = "b" * dimensionless
#     res = a ** -b

#     assert str(res) == "a**(-b) meters**(-b)"


# def test_pow_sym_cancels():
#     a = "a" * meters
#     b = "b" * dimensionless
#     res = (a ** b ) * (a ** -b)

#     assert str(res) == "1"


def test_pow_neg_100():
    a = "a" * meters
    res = a ** -100

    assert str(res) == "a**(-100) meters**(-100)"


def test_pow_zero():
    a = "a" * meters
    res = a ** 0

    assert str(res) == "1"


def test_pow_newton_meters_2():
    a = "a" * newton * meters
    res = a ** 2

    # TODO: this test should actually fail - the regex is wrong
    assert str(res) == "a**2 meters**2*newton**2"


def test_pow_int_meters_fails():
    b = 5 * meters

    try:
        2 ** b
        assert False

    except DimensionalExponentError as e:
        assert True