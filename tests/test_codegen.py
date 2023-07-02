from mathpad import *

def test_as_numpy_func_nums():
    x = "x" * m
    y = "y" * m
    z = "z" * m
    f = mathpad.codegen.as_numpy_func(x + y + z)
    res = f({x: 1, y: 2, z: 3})
    assert res == 6

def test_as_numpy_func_arraylikes():
    x = "x" * m
    y = "y" * m
    z = "z" * m
    f = mathpad.codegen.as_numpy_func(x + y + z)
    res = f({x: [1, 2, 3], y: [1, 2, 3], z: [1, 2, 3]})
    assert (res == [3, 6, 9]).all()