from mathpad import *


def test_var_meters():
    a = var("a", meters)
    assert str(a) == "a meters"
    assert a.units == meters.units


def test_var_vel_rads():
    weird_unit = meters / seconds * radians
    a = var("a", weird_unit)
    assert str(a) == "a meter*radians/second"
    assert a.units == weird_unit.units


def test_solve1_meters_eq_float():
    float_val = 1.2345
    a = var("a", meters)
    res = solve(a, a == float_val)

    assert isinstance(res, Solution)
    assert res[a].val == float_val
    assert res[a].units == a.units


def test_solve1_meters_eq_meters_plus_kilometers():
    a = 10 * meters
    b = 2 * kilometers
    c = var("c", meters)
    res = solve(c, c == a + b)

    assert isinstance(res, Solution)
    assert res[c] == "2010 kilometers"
