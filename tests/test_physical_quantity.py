from mathpad import *


def test_mul_meters_int():
    a = 10 * meters
    res = a * 5
    assert res.val == 50
    assert res.units == meters.units


def test_mul_int_meters():
    a = 10 * meters
    res = 5 * a
    res = a * 5
    assert res.val == 50
    assert res.units == meters.units


def test_mul_meters_seconds():
    a = 10 * meters
    b = 5 * seconds
    res = a * b
    assert res.val == 50
    assert res.units == meter.units * second.units


def test_mul_meters_meters():
    a = 10 * meters
    b = 5 * meters
    res = a * b
    assert res.val == 50
    assert res.units == meter.units * meter.units


def test_div_meters_int():
    a = 10 * meters
    res = a / 5
    assert res.val == 2
    assert res.units == meters.units


def test_div_int_meters():
    a = 10 * meters
    res = 50 / a
    assert res.val == 5
    assert res.units == meters.units ** -1 == 1 / meters.units


def test_div_meters_seconds():
    a = 10 * meters
    b = 5 * seconds
    res = a / b
    assert res.val == 2
    assert res.units == meter.units / second.units


def test_div_meters_meters():
    a = 10 * meters
    b = 5 * meters
    res = a / b
    assert res.val == 2
    assert res.units == 1
