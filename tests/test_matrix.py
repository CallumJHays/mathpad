
from mathpad import *

from _test_utils import expect_err
from mathpad.core.val import DimensionError

def test_Matrix_construct_R2xR2():

    A = Mat[R2("L"), R2("R")](
        [1, 2],
        [3, 4]
    )

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[1, 0] == 3).eval()
    assert (A[1, 1] == 4).eval()

def test_Matrix_construct_R2xR3():
    
    A = Mat[R2("L"), R3("R")](
        [1, 2, 3],
        [4, 5, 6]
    )

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[0, 2] == 3).eval()
    assert (A[1, 0] == 4).eval()
    assert (A[1, 1] == 5).eval()
    assert (A[1, 2] == 6).eval()


def test_Matrix_construct_R3xR2():
    
    A = Mat[R3("A"), R2("B")](
        [1, 2],
        [3, 4],
        [5, 6]
    )

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 2).eval()
    assert (A[1, 0] == 3).eval()
    assert (A[1, 1] == 4).eval()
    assert (A[2, 0] == 5).eval()
    assert (A[2, 1] == 6).eval()


def test_Matrix_construct_R3xR3():
    A = Mat[R3("A"), R3("B")](
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9)
    )

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
        Mat[R2("A"), R3("B")](
            (1, 2, 3),
            (4, 5 * v, 6)
        )

def test_Matrix_R2xR2m():
    A = Mat[R2("A"), R2("B") * m](
        (1 * m, 2 * m),
        (3 * m, 4 * m)
    )

    assert (A[0, 0] == 1 * m).eval()
    assert (A[0, 1] == 2 * m).eval()
    assert (A[1, 0] == 3 * m).eval()
    assert (A[1, 1] == 4 * m).eval()

def test_Matrix_incorrect_units_no_check():
    A = Mat[R2("A"), R3("B") * m](
        (1 * amperes, 2, 3),
        (4, 5 * v, 6 * N),

        check=False
    )

    assert (A[0, 0] == 1 * m).eval()
    assert (A[0, 1] == 2 * m).eval()
    assert (A[0, 2] == 3 * m).eval()
    assert (A[1, 0] == 4 * m).eval()
    assert (A[1, 1] == 5 * m).eval()
    assert (A[1, 2] == 6 * m).eval()

def test_Matrix_identity():
    A = Mat[R2("A"), R2("B")].I

    assert (A[0, 0] == 1).eval()
    assert (A[0, 1] == 0).eval()
    assert (A[1, 0] == 0).eval()
    assert (A[1, 1] == 1).eval()

def test_Matrix_identity_nonsquare_fails():
    with expect_err(AssertionError):
        Mat[R2("A"), R3("B")].I

def test_Matrix_add_Mat():
    L = R2("L")
    R = R2("R")
    A = Mat[L, R](
        (1, 2),
        (3, 4)
    )

    B = Mat[L, R](
        (5, 6),
        (7, 8)
    )

    C = A + B

    assert (C[0, 0] == 6).eval()
    assert (C[0, 1] == 8).eval()
    assert (C[1, 0] == 10).eval()
    assert (C[1, 1] == 12).eval()

def test_Matrix_sub_Mat():
    A = R2("A")
    B = R2("B")

    C = Mat[A, B](
        (1, 2),
        (3, 4)
    )

    D = Mat[A, B](
        (5, 6),
        (7, 8)
    )

    E = C - D

    assert (E[0, 0] == -4).eval()
    assert (E[0, 1] == -4).eval()
    assert (E[1, 0] == -4).eval()
    assert (E[1, 1] == -4).eval()

def test_Matrix_matmul_Mat():
    O1 = R2("O1")
    O2 = R2("O2")
    O3 = R2("O3")
    
    A = Mat[O1, O2](
        (1, 2),
        (3, 4)
    )

    B = Mat[O2, O3](
        (5, 6),
        (7, 8)
    )

    C = A @ B

    assert (C[0, 0] == 19).eval()
    assert (C[0, 1] == 22).eval()
    assert (C[1, 0] == 43).eval()
    assert (C[1, 1] == 50).eval()
    assert C.left_frame == O1
    assert C.right_frame == O3

def test_Matrix_matmul_Vector():
    O1 = R2("O1")
    O2 = R2("O2")

    A = Mat[O1, O2](
        (1, 2),
        (3, 4)
    )

    v = O2[5, 6]

    C = A @ v

    assert (C[0] == 17).eval()
    assert (C[1] == 39).eval()
    assert C.frame == O1

def test_Vector_matmul_Mat():
    O1 = R2("O1")
    O2 = R2("O2")
    A = Mat[O1, O2](
        (1, 2),
        (3, 4)
    )

    v = O1[5, 6]

    C = v @ A

    assert (C[0] == 23).eval()
    assert (C[1] == 34).eval()
    assert C.frame == O2


def test_Matrix_mul_Dimensionless():
    A = Mat[R2("L"), R2("R")](
        (1, 2),
        (3, 4)
    )

    B = A * 2

    assert (B[0, 0] == 2).eval()
    assert (B[0, 1] == 4).eval()
    assert (B[1, 0] == 6).eval()
    assert (B[1, 1] == 8).eval()
    assert B.left_frame == A.left_frame
    assert B.right_frame == A.right_frame


def test_Dimensionless_mul_Mat():
    A = Mat[R2("L"), R2("R")](
        (1, 2),
        (3, 4)
    )

    B = 2 * A

    assert (B[0, 0] == 2).eval()
    assert (B[0, 1] == 4).eval()
    assert (B[1, 0] == 6).eval()
    assert (B[1, 1] == 8).eval()
    assert B.left_frame == A.left_frame
    assert B.right_frame == A.right_frame


def test_Matrix_mul_Val():
    A = Mat[R2("A"), R2("B")](
        (1, 2),
        (3, 4)
    )

    b = 2 * m
    C = A * b

    assert (C[0, 0] == 2 * m).eval()
    assert (C[0, 1] == 4 * m).eval()
    assert (C[1, 0] == 6 * m).eval()
    assert (C[1, 1] == 8 * m).eval()
    assert C.left_frame == A.left_frame
    assert C.right_frame == A.right_frame * m

def test_Val_mul_Mat():
    A = Mat[R2("A"), R2("B")](
        (1, 2),
        (3, 4)
    )

    b = 2 * m
    C = b * A

    assert (C[0, 0] == 2 * m).eval()
    assert (C[0, 1] == 4 * m).eval()
    assert (C[1, 0] == 6 * m).eval()
    assert (C[1, 1] == 8 * m).eval()
    assert C.left_frame == A.left_frame
    assert C.right_frame == A.right_frame * m


def test_Matrix_constructor_syms():

    a, b, c, d = [
        c * dimensionless
        for c in "abcd"
    ]

    A = Mat[R2("A"), R2("B")](
        (a, b),
        (c, d)
    )

    assert (A[0, 0] == a).eval()
    assert (A[0, 1] == b).eval()
    assert (A[1, 0] == c).eval()
    assert (A[1, 1] == d).eval()

def test_Matrix_symbolic():
    A = Mat[R2("L"), R2("R")]("A")
    elements = [el for row in A for el in row]

    assert len(elements) == 4
    assert elements[0] == A[0, 0]
    assert elements[1] == A[0, 1]
    assert elements[2] == A[1, 0]
    assert elements[3] == A[1, 1]

