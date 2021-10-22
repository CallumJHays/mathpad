from typing import (
    Any,
    OrderedDict,
    Union,
)

from sympy.vector import CoordSys3D

from mathpad.physical_quantity import (
    PhysicalQuantity,
)

R3 = CoordSys3D("ℝ3")


class VectorSpace(PhysicalQuantity):
    def __init__(self, ordered_units: OrderedDict[str, PhysicalQuantity]):
        self.ordered_units = ordered_units

    def __getattribute__(self, name: str) -> Any:
        return self.ordered_units.get(name)

    def __iter__(self):
        return self.ordered_units.values()

    def __getitem__(self, idx: Union[int, slice]):
        ords: OrderedDict[str, PhysicalQuantity] = self.ordered_units
        return list(ords.values())[idx]


# class Vector(PhysicalQuantity):
#     # TODO: review typing once PEP TypeVarTuple lands
#     def __new__(self, vector_space, val: Iterable[PhysicalQuantity]):
#         super().__init__(units, val)

# def vector_var(
#     name: str, vector_space: Union[VectorSpace, OrderedDict[str, PhysicalQuantity]]
# ) -> Vector:
#     sym = sympy.Symbol(name, **assumptions)
#     if not isinstance(vector_space, VectorSpace):
#         vector_space = VectorSpace(vector_space)
#     res =

#     return res
