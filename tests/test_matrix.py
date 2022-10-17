
from mathpad import *

from _test_utils import expect_err

def test_Matrix_construct_R2xR2():
    A = Matrix(R2("A"), R2("B"), [
        (1, 2),
        (3, 4)
    ])

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[1, 0] == 3).eval()
    assert (A[1, 1] == 4).eval()

def test_Matrix_construct_R2xR3():
    A = Matrix(R2("A"), R3("B"), [
        (1, 2, 3),
        (4, 5, 6)
    ])

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[0, 2] == 3).eval()
    assert (A[1, 0] == 4).eval()
    assert (A[1, 1] == 5).eval()
    assert (A[1, 2] == 6).eval()


def test_Matrix_construct_R3xR2():
    A = Matrix(R3("A"), R2("B"), [
        (1, 2),
        (3, 4),
        (5, 6)
    ])

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[1, 0] == 3).eval()
    assert (A[1, 1] == 4).eval()
    assert (A[2, 0] == 5).eval()
    assert (A[2, 1] == 6).eval()


def test_Matrix_construct_R3xR3():
    A = Matrix(R3("A"), R3("B"), [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9)
    ])

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[0, 2] == 3).eval()
    assert (A[1, 0] == 4).eval()
    assert (A[1, 1] == 5).eval()
    assert (A[1, 2] == 6).eval()
    assert (A[2, 0] == 7).eval()
    assert (A[2, 1] == 8).eval()
    assert (A[2, 2] == 9).eval()

def test_Matrix_incorrect_units():
    with expect_err(DimensionError):
        Matrix(R2("A"), R3("B"), [
            (1, 2, 3),
            (4, 5 * v, 6)
        ])

def test_Matrix_R2xR2m():
    A = Matrix(R2("A"), R2("B") * m, [
        (1 * m, 2 * m),
        (3 * m, 4 * m)
    ])

    assert (A[0, 0] == 1 * m).eval()
    assert (A[0, 1] == 2 * m).eval()
    assert (A[1, 0] == 3 * m).eval()
    assert (A[1, 1] == 4 * m).eval()

def test_Matrix_incorrect_units_no_check():
    A = Matrix(R2("A"), R3("B") * m, [
        (1 * amperes, 2, 3),
        (4, 5 * v, 6 * N)
    ], check_val_dims=False)

    assert (A[0, 0] == 1 * m).eval()
    assert (A[0, 1] == 2 * m).eval()
    assert (A[0, 2] == 3 * m).eval()
    assert (A[1, 0] == 4 * m).eval()
    assert (A[1, 1] == 5 * m).eval()
    assert (A[1, 2] == 6 * m).eval()

def test_Matrix_identity():
    A = Matrix.identity(R2("A"), R2("B"))

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 0).eval()
    assert (A[1, 0] == 0).eval()
    assert (A[1, 1] == 1).eval()

def test_Matrix_identity_nonsquare_fails():
    with expect_err(AssertionError):
        Matrix.identity(R2("A"), R3("B"))

def test_Matrix_add_Matrix():
    A = Matrix(R2("A"), R2("B"), [
        (1, 2),
        (3, 4)
    ])

    B = Matrix(R2("A"), R2("B"), [
        (5, 6),
        (7, 8)
    ])

    C = A + B

    assert (C[0, 0] == 6).eval()
    assert (C[0, 1] == 8).eval()
    assert (C[1, 0] == 10).eval()
    assert (C[1, 1] == 12).eval()

def test_Matrix_sub_Matrix():
    A = Matrix(R2("A"), R2("B"), [
        (1, 2),
        (3, 4)
    ])

    B = Matrix(R2("A"), R2("B"), [
        (5, 6),
        (7, 8)
    ])

    C = A - B

    assert (C[0, 0] == -4).eval()
    assert (C[0, 1] == -4).eval()
    assert (C[1, 0] == -4).eval()
    assert (C[1, 1] == -4).eval()

def test_Matrix_matmul_Matrix():
    O1 = R2("O1")
    O2 = R2("O2")
    O3 = R2("O3")
    
    A = Matrix(O1, O2, [
        (1, 2),
        (3, 4)
    ])

    B = Matrix(O2, O3, [
        (5, 6),
        (7, 8)
    ])

    C = A @ B

    assert (C[0, 0] == 19).eval()
    assert (C[0, 1] == 22).eval()
    assert (C[1, 0] == 43).eval()
    assert (C[1, 1] == 50).eval()
    assert C.left_space == O1
    assert C.right_space == O3

def test_Matrix_matmul_Vector():
    O1 = R2("O1")
    O2 = R2("O2")
    A = Matrix(O1, O2, [
        (1, 2),
        (3, 4)
    ])

    v = O2[5, 6]

    C = A @ v

    assert (C[0] == 17).eval()
    assert (C[1] == 39).eval()
    assert C.space == O1

def test_Vector_matmul_Matrix():
    O1 = R2("O1")
    O2 = R2("O2")
    A = Matrix(O1, O2, [
        (1, 2),
        (3, 4)
    ])

    v = O1[5, 6]

    C = v @ A

    assert (C[0] == 23).eval()
    assert (C[1] == 34).eval()
    assert C.space == O2


def test_Matrix_mul_Dimensionless():
    A = Matrix(R2(), R2(), [
        (1, 2),
        (3, 4)
    ])

    B = A * 2

    assert (B[0, 0] == 2).eval()
    assert (B[0, 1] == 4).eval()
    assert (B[1, 0] == 6).eval()
    assert (B[1, 1] == 8).eval()
    assert B.left_space == A.left_space
    assert B.right_space == A.right_space


def test_Dimensionless_mul_Matrix():
    A = Matrix(R2(), R2(), [
        (1, 2),
        (3, 4)
    ])

    B = 2 * A

    assert (B[0, 0] == 2).eval()
    assert (B[0, 1] == 4).eval()
    assert (B[1, 0] == 6).eval()
    assert (B[1, 1] == 8).eval()
    assert B.left_space == A.left_space
    assert B.right_space == A.right_space


def test_Matrix_mul_Val():
    A = Matrix(R2(), R2(), [
        (1, 2),
        (3, 4)
    ])

    b = 2 * m
    C = A * b

    assert (C[0, 0] == 2 * m).eval()
    assert (C[0, 1] == 4 * m).eval()
    assert (C[1, 0] == 6 * m).eval()
    assert (C[1, 1] == 8 * m).eval()
    assert C.left_space == A.left_space
    assert C.right_space == A.right_space * m

def test_Val_mul_Matrix():
    A = Matrix(R2(), R2(), [
        (1, 2),
        (3, 4)
    ])

    b = 2 * m
    C = b * A

    assert (C[0, 0] == 2 * m).eval()
    assert (C[0, 1] == 4 * m).eval()
    assert (C[1, 0] == 6 * m).eval()
    assert (C[1, 1] == 8 * m).eval()
    assert C.left_space == A.left_space
    assert C.right_space == A.right_space * m


def test_Matrix_constructor_syms():

    a, b, c, d = [
        c * dimensionless
        for c in "abcd"
    ]

    A = Matrix(R2(), R2(), [
        (a, b),
        (c, d)
    ])

    assert (A[0, 0] == a).eval()
    assert (A[0, 1] == b).eval()
    assert (A[1, 0] == c).eval()
    assert (A[1, 1] == d).eval()

def test_Matrix_symbolic():
    A = Matrix(R2(), R2(), "A")
