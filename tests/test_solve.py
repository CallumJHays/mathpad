from mathpad import *


def test_var_meters():
    a = "a" * meters
    assert str(a) == "a meters"
    assert a.units == meters.units


def test_var_vel_rads():
    weird_unit = meters / seconds * radians
    a = "a" * weird_unit
    assert str(a) == "a meter*radians/second"
    assert a.units == weird_unit.units


def test_solve1_meters_eq_float():
    float_val = 1.2345
    a = "a" * meters
    slns = solve([a == float_val], [a])

    assert len(slns) == 1
    sln = slns[0]

    assert isinstance(sln, Solution)
    assert sln[a].expr == float_val
    assert sln[a].units == a.units


def test_solve1_meters_eq_meters_plus_kilometers():
    a = 10 * meters
    b = 2 * kilometers
    c = "c" * meters
    slns = solve([c == a + b], [c])

    assert len(slns) == 1
    sln = slns[0]

    assert isinstance(sln, Solution)
    assert sln[c].expr == 2010
    assert sln[c].units == c.units
