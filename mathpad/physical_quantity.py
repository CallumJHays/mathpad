from abc import ABC
from re import U
from typing import Any, Callable, Collection, Tuple, Union, TypeVar, overload

import sympy
import sympy.physics.units as su
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units.unitsystem import UnitSystem
from sympy.physics.units.util import quantity_simplify, convert_to
from sympy.polys.polytools import factor_list

# TODO: support numpy arrays
Num = Union[int, float, complex]

# this should be a classmethod, but it isn't
_get_dimensional_expr = UnitSystem.get_default_unit_system().get_dimensional_expr


class PhysicalQuantity:
    "An object representing a physical quantity. For example 10 Ohms or 20 meters / second**2"

    dimension: su.Dimension = None  # type: ignore

    def __init__(
        self,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,
    ):
        self.val = val
        self.units: su.Quantity = quantity_simplify(units)
        units_dimension = _get_dimensional_expr(self.units)

        if self.dimension is None:
            assert (
                self.__class__ is PhysicalQuantity
            ), "Subclasses of PhysicalQuantity must specify the 'dimension' class variable"
            self.dimension = units_dimension  # type: ignore

        else:
            assert dimsys_SI.equivalent_dims(units_dimension, self.dimension), (
                f"Units {self.units} do not match the dimensionality of {self.__class__.__name__} ({self.dimension}).\n"
                f"Instead got {units_dimension}"
            )

    def __hash__(self):
        return hash(self.val)

    def __eq__(self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]") -> "Equation":
        if isinstance(other, PhysicalQuantity):
            self.check_same_dimensions(other)
        return Equation(self, other)

    def __req__(self, other: Num) -> "Equation":
        return Equation(other, self)

    def __repr__(self) -> str:
        return self._repr(True)

    def _repr(self, with_units: bool) -> str:
        res = f"{self.val.evalf(n=5) if isinstance(self.val, sympy.Expr) else self.val}"
        if with_units:
            res += f" {self.units}"
        return res

    def check_same_dimensions(self, other: "PhysicalQuantity"):
        assert self.has_same_dimensions(
            other
        ), "This operation requires operands to have the same dimensionality"

    def has_same_dimensions(self, other: "PhysicalQuantity") -> bool:
        return dimsys_SI.equivalent_dims(self.dimension, other.dimension)

    def _op(
        self,
        other: "Q[PhysicalQuantity]",
        op: Callable[[Any, Any], Any],
        homogeneous: bool = False,
        is_pow: bool = False,  # oops, leaky abstraction!
    ) -> "PhysicalQuantity":
        # normalize inputs
        if isinstance(other, PhysicalQuantity):
            if homogeneous:
                self.check_same_dimensions(other)

            other_units = other.units
            other_val = other.val
            other_dim = other.dimension
        else:
            other_units = other if is_pow else 1
            other_val = other
            other_dim = other if is_pow else 1

        new_units = quantity_simplify(op(self.units, other_units))

        # move the factor from unit conversion from units to the value
        units_factor, new_units = _handle_unit_scaling(new_units)
        new_val = units_factor * op(self.val, other_val)

        if (
            homogeneous
            or (
                (not isinstance(other, PhysicalQuantity))
                or su.Dimension(other.dimension).is_dimensionless
            )
            and not is_pow
        ):
            return self.__class__(new_units, new_val)

        else:
            return PhysicalQuantity(new_units, new_val, op(self.dimension, other_dim))

    def in_units(
        self: "GPhysicalQuantity", units: Union[str, "GPhysicalQuantity"]
    ) -> "GPhysicalQuantity":
        if isinstance(units, str):
            new_units = UnitSystem.get_unit_system("SI")._base_units

        else:
            self.check_same_dimensions(units)
            new_units = units.units

        units_factor, new_units = _handle_unit_scaling(
            convert_to(self.units, new_units)
        )  # type: ignore
        new_val = units_factor * self.val

        if self.__class__ is PhysicalQuantity:
            return PhysicalQuantity(new_units, new_val, self.dimension)
        else:
            # no need to pass dimension - subclasses should define their own.
            return self.__class__(new_units, new_val)

    @overload
    def __mul__(self, other: "PhysicalQuantity") -> "PhysicalQuantity":
        ...

    @overload
    def __mul__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    def __mul__(self, other: "Q[PhysicalQuantity]") -> "PhysicalQuantity":
        # normalize inputs
        other_units, other_val = (
            (other.units, other.val)
            if isinstance(other, PhysicalQuantity)
            else (1, other)
        )
        return PhysicalQuantity(self.units * other_units, self.val * other_val)  # type: ignore

    # because matrix multiplication has its own operator, multiplication can be commutative
    # sympy also reorders everything under the hood (alphabetically, I believe; so preserving order is pointless)
    __rmul__ = __mul__

    @overload
    def __truediv__(self, other: "PhysicalQuantity") -> "PhysicalQuantity":
        ...

    @overload
    def __truediv__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    def __truediv__(self, other: "Q[PhysicalQuantity]") -> "PhysicalQuantity":
        # normalize inputs
        other_units, other_val = (
            (other.units, other.val)
            if isinstance(other, PhysicalQuantity)
            else (1, other)
        )
        return PhysicalQuantity(self.units / other_units, self.val / other_val)  # type: ignore

    def __rtruediv__(self, other: "Q[PhysicalQuantity]") -> "PhysicalQuantity":
        # normalize inputs
        other_units, other_val = (
            (other.units, other.val)
            if isinstance(other, PhysicalQuantity)
            else (1, other)
        )
        return PhysicalQuantity(other_units / self.units, other_val / self.val)  # type: ignore

    # exponents should always be dimensionless
    def __pow__(self, other: "Q[PhysicalQuantity]") -> "PhysicalQuantity":
        if isinstance(other, PhysicalQuantity):
            assert su.Dimension(other.dimension).is_dimensionless
        return self._op(other, lambda a, b: a ** b, is_pow=True)

    def __rpow__(self, other: Num) -> "PhysicalQuantity":
        assert su.Dimension(self.dimension).is_dimensionless
        return self._op(other, lambda a, b: b ** a, is_pow=True)

    def __add__(
        self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]"
    ) -> "GPhysicalQuantity":
        return self._op(other, lambda a, b: a + b, True)

    def __sub__(
        self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]"
    ) -> "GPhysicalQuantity":
        return self._op(other, lambda a, b: a - b, True)


GPhysicalQuantity = TypeVar("GPhysicalQuantity", bound=PhysicalQuantity)
Q = Union[GPhysicalQuantity, Num]


class Equation:
    def __init__(self, lhs: Q[GPhysicalQuantity], rhs: Q[GPhysicalQuantity]):
        assert isinstance(lhs, PhysicalQuantity) or isinstance(rhs, PhysicalQuantity)

        self.units = lhs.units if isinstance(lhs, PhysicalQuantity) else rhs.units

        if isinstance(lhs, PhysicalQuantity) and isinstance(rhs, PhysicalQuantity):
            # rescale the rhs to match units
            rhs = rhs.in_units(lhs)
            # sanity check
            assert lhs.units == self.units == rhs.units

        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        res = (
            self.lhs._repr(False)
            if isinstance(self.lhs, PhysicalQuantity)
            else str(self.lhs)
        )
        res += " = "
        res += (
            self.rhs._repr(False)
            if isinstance(self.rhs, PhysicalQuantity)
            else str(self.rhs)
        )
        res += f" {self.units}"
        return res

    def as_sympy_eq(self) -> sympy.Equality:
        return sympy.Equality(self.lhs.val, self.rhs.val)

    def as_units_eq_without_unknowns(self, unknowns: Collection[PhysicalQuantity]):
        return sympy.Equality(self.lhs.units, self.rhs.units)


def _handle_unit_scaling(unit_expr: sympy.Expr) -> Tuple[float, Any]:
    # TODO: verify; will getting the first factor always work?
    units_factor = factor_list(unit_expr)[0]
    new_units = quantity_simplify(unit_expr / units_factor)
    return units_factor, new_units


def units_equivalent(a: sympy.Expr, b: sympy.Expr) -> bool:
    return True