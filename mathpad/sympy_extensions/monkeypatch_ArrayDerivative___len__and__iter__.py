
from typing import Iterator, Union
from typing_extensions import Never
from sympy import Derivative, diff
from sympy.tensor.array.array_derivatives import ArrayDerivative
from .monkeypatch import monkeypatch_method

@monkeypatch_method(ArrayDerivative)
def __len__(self: ArrayDerivative):
    assert len(self.shape) == 2 and self.shape[1] == 1, \
        f"getting len() of ArrayDerivative must be a column vector. Got tensor of shape: {self.shape}"
    return self.shape[0]

# @monkeypatch_method(ArrayDerivative)
# def __iter__(self: ArrayDerivative) -> Iterator[Derivative]:
#     """
#     iterate over the ArrayDerivative, yielding:

#     ```
#     A = self.expr # underlying expression
#     (Derivative(A[i, 0]) for i in range(len(self)))
#     ```

#     in the case of column vectors, or:

#     ```
#     A = self.expr
#     (Derivative(A[i, :, :, ...]) for i in range(len(self)))
#     ```

#     iterating over any other tensor will raise NotImplementedError
#     """

#     if len(self.shape) == 2 and self.shape[1] == 1:
#         # column vector
#         return (
#             diff(self.expr[i, 0], *self.variable_count)
#             for i in range(len(self)) # type: ignore [attr-defined]
#         )
    
#     else:
#         # higher order tensors TODO
#         raise NotImplementedError("TODO: implement iteration over higher order tensors (Matrix+)")

@monkeypatch_method(ArrayDerivative)
def __getitem__(self: ArrayDerivative, index: int) -> Union[Derivative, Never]:
    if len(self.shape) == 2 and self.shape[1] == 1:
        return diff(self.expr[index, 0], *self.variable_count)
    else:
        # higher order tensors TODO
        raise NotImplementedError("TODO: implement iteration over higher order tensors (Matrix+)")