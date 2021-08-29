from typing import Any, Tuple, Union, TypeVar, overload, Callable
import re
from abc import ABC

import sympy
import sympy.physics.units as su
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units.unitsystem import UnitSystem
from sympy.physics.units.util import (
    quantity_simplify,
    convert_to,
)

from mathpad.equation import Equation

# TODO: support numpy arrays
Num = Union[int, float, complex]
_UNSET = ()

# this should be a classmethod, but it isn't
_units2dimension = UnitSystem.get_default_unit_system().get_dimensional_expr


class AbstractPhysicalQuantity(ABC):
    "An object representing a physical quantity. For example 10 ohms or 20 meters / second**2"

    dimension: su.Dimension = _UNSET  # type: ignore

    def __init_subclass__(cls):
        assert cls.dimension is not _UNSET
        super().__init_subclass__()

    def __init__(
        self,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,
    ):

        self.val = val
        self.units: su.Quantity = quantity_simplify(units) if units != 1 else 1

        assert not self.dimension is _UNSET
        units_dimension = _units2dimension(self.units)

        if _is_dimensionless(self.dimension) and _is_dimensionless(units_dimension):
            return

        else:
            assert dimsys_SI.equivalent_dims(units_dimension, self.dimension), (
                f"Units {self.units} do not match the dimensionality of {self.__class__.__name__} ({self.dimension}).\n"
                f"Instead got {units_dimension}"
            )

    def __hash__(self):
        return hash(self.val)

    @overload
    def __eq__(self, other: "PhysicalQuantity") -> "Equation":
        ...

    @overload
    def __eq__(self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]") -> "Equation":
        ...

    def __eq__(self, other: "Q[AbstractPhysicalQuantity]") -> "Equation":
        if isinstance(other, AbstractPhysicalQuantity):
            SumDimensionsMismatch.check(self, "==", other)
        return Equation(self, other)

    def __req__(self, other: Num) -> "Equation":
        return Equation(other, self)

    def __repr__(self) -> str:
        return self._repr(True)

    def _repr(self, with_units: bool) -> str:
        # ignore 0's following last non-zero decimal
        res = re.sub(
            r"(\d+\.\d*[^0])0+",
            r"\1",
            str(self.val if _is_primitive_num(self.val) else self.val.evalf(6)),  # type: ignore
        )
        res = re.sub(r"\.0+([e\*]|$)", r"\1", res)

        # also ignore 1*x
        res = re.sub(r"1\*", "", res)

        # do surgery to get display how we want it with very specific rules
        # not going to work for complex expressions TODO: make it

        if with_units and self.units != 1:
            units_str = re.sub(
                r"(.*?[a-zA-Z])(\/|\*\*|$)", r"\1s\2", str(self.units), 1
            )

            res += f" {units_str}"

        # TODO: use superscript for exponents (both val and units)

        return res

    def in_units(
        self: "GPhysicalQuantity", units: Union[str, "GPhysicalQuantity"]
    ) -> "GPhysicalQuantity":
        if isinstance(units, str):
            if units == "si":
                units = "SI"
            new_units = UnitSystem.get_unit_system(units)._base_units

        else:
            SumDimensionsMismatch.check(self, ".in_units", units)
            new_units = units.units

        units_factor, new_units = _split_coeff_and_units(
            convert_to(self.units, new_units)  # type: ignore
        )
        new_val = units_factor * self.val

        return self.__class__(new_units, new_val)

    def __add__(self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]"):
        return self._sum_op(other, lambda a, b: a + b, "+", False)

    def __radd__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        return self._sum_op(other, lambda a, b: b + a, "+", True)

    def __sub__(self: "GPhysicalQuantity", other: "Q[GPhysicalQuantity]"):
        return self._sum_op(other, lambda a, b: a - b, "-", False)

    def __rsub__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        return self._sum_op(other, lambda a, b: b - a, "-", True)

    @overload
    def __mul__(self, other: "AbstractPhysicalQuantity") -> "PhysicalQuantity":
        ...

    @overload
    def __mul__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    def __mul__(self, other: "Q[AbstractPhysicalQuantity]") -> "PhysicalQuantity":
        return self._prod_op(other, lambda a, b: a * b, is_pow=False)

    # because matrix multiplication has its own operator, multiplication can be commutative
    # sympy also reorders everything under the hood (alphabetically, I believe; so preserving order is pointless)
    __rmul__ = __mul__

    @overload
    def __truediv__(self, other: "AbstractPhysicalQuantity") -> "PhysicalQuantity":
        ...

    @overload
    def __truediv__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    def __truediv__(self, other: "Q[AbstractPhysicalQuantity]") -> "PhysicalQuantity":
        return self._prod_op(other, lambda a, b: a / b, is_pow=False)

    def __rtruediv__(self, other: Num) -> "PhysicalQuantity":
        return self._prod_op(other, lambda a, b: b / a, is_pow=False)

    # exponents should always be dimensionless
    def __pow__(self, other: "Q[AbstractPhysicalQuantity]") -> "PhysicalQuantity":
        if isinstance(other, AbstractPhysicalQuantity) and not _is_dimensionless(
            other.dimension
        ):
            raise DimensionalExponentError(
                f"Exponents must always be dimensionless. [{other.dimension}: {other}]"
            )
        return self._prod_op(other, lambda a, b: a ** b, is_pow=True)

    def __rpow__(self, other: Num) -> "Dimensionless":
        if not isinstance(self, Dimensionless):
            raise DimensionalExponentError(
                f"Exponents must always be dimensionless. [{self.dimension}: {self}]"
            )

        res = self._prod_op(other, lambda a, b: b ** a, is_pow=True)

        assert isinstance(res, Dimensionless)
        return res

    def _sum_op(
        self: "GPhysicalQuantity",
        other: "Q[GPhysicalQuantity]",
        op: Callable[[Any, Any], Any],
        op_str: str,
        reverse: bool,
    ) -> "GPhysicalQuantity":
        other_units, other_val = (
            (other.units, other.val)
            if isinstance(other, AbstractPhysicalQuantity)
            else (self.units, other)
        )

        if isinstance(other, AbstractPhysicalQuantity):
            SumDimensionsMismatch.check(
                other if reverse else self, op_str, self if reverse else other
            )

        other_units_rescale_factor = float(quantity_simplify(other_units / self.units))

        # choose the larger of the two input units as the output units
        use_other_units = other_units_rescale_factor > 1
        new_units = other_units if use_other_units else self.units

        self_val_rescaled = (
            self.val / other_units_rescale_factor if use_other_units else self.val
        )
        other_val_rescaled = (
            other_val if use_other_units else other_val * other_units_rescale_factor
        )

        new_val = op(self_val_rescaled, other_val_rescaled)

        return self.__class__(new_units, new_val)

    def _prod_op(
        self,
        other: "Q[AbstractPhysicalQuantity]",
        op: Callable[[Any, Any], Any],
        is_pow: bool,
    ) -> "PhysicalQuantity":
        other_units, other_val = (
            (other.units, other.val)
            if isinstance(other, AbstractPhysicalQuantity)
            else (other if is_pow else 1, other)
        )

        rescale_factor, new_units = _split_coeff_and_units(op(self.units, other_units))

        new_val = rescale_factor * op(self.val, other_val)
        if isinstance(new_val, sympy.Expr):
            new_val = quantity_simplify(new_val)

        dimension_unchanged = dimsys_SI.equivalent_dims(
            self.dimension, _units2dimension(new_units)
        )

        if dimension_unchanged:
            return self.__class__(new_units, new_val)  # type: ignore

        elif new_units == Dimensionless.default_units:
            return Dimensionless(Dimensionless.default_units, new_val)  # type: ignore

        else:
            # TODO: a big lookup table for dimensional expr -> AbstractPhysicalQuantity subclass
            return PhysicalQuantity(new_units, new_val)  # type: ignore


GPhysicalQuantity = TypeVar("GPhysicalQuantity", bound=AbstractPhysicalQuantity)
Q = Union[GPhysicalQuantity, Num]


class DimensionError(TypeError):
    pass


class DimensionalExponentError(DimensionError):
    pass


class SumDimensionsMismatch(DimensionError):
    def __init__(
        self,
        left: AbstractPhysicalQuantity,
        operation: str,
        right: AbstractPhysicalQuantity,
        extra_msg: str = "",
    ):
        self.args = (
            f'{extra_msg}[{left.dimension}: {left}] "{operation}" [{right.dimension}: {right}]',
        )

    @classmethod
    def check(
        cls, a: AbstractPhysicalQuantity, op_str: str, b: AbstractPhysicalQuantity
    ):
        if not dimsys_SI.equivalent_dims(a.dimension, b.dimension):
            raise cls(a, op_str, b)


def _split_coeff_and_units(unit_expr: sympy.Expr) -> Tuple[float, Any]:
    # TODO: test and refactor
    converted = quantity_simplify(unit_expr)  # type: ignore
    if converted.is_Number:
        return converted, Dimensionless.default_units  # type: ignore

    try:
        units_factor = converted.args[0]
        if units_factor.is_Number:
            return units_factor, quantity_simplify(unit_expr / units_factor)

    except AttributeError:
        pass

    return 1, unit_expr


def _is_primitive_num(x: Q[AbstractPhysicalQuantity]):
    return isinstance(x, (int, float, complex))


class Dimensionless(AbstractPhysicalQuantity):
    dimension = su.Dimension(1)
    default_units = 1


class PhysicalQuantity(AbstractPhysicalQuantity):
    """A physical quantity whose dimensionality cannot be type-hinted, but will still check at runtime.
    Subclasses `Dimensionless` for type-checking reasons; doesn't have to be dimensionless
    """

    dimension = None  # gets set in __init__

    def __new__(
        cls,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,
    ):
        dimension = _units2dimension(units)

        if _is_dimensionless(dimension):
            res = Dimensionless(units, val)

        else:
            res = super().__new__(cls)
            res.dimension = dimension

        return res


def _is_dimensionless(dimension):
    from mathpad.physical_quantities import Angle, AngularMil, SteRadian

    return (
        any(
            dimension == dim
            for dim in {
                1,
                Angle.dimension,
                Dimensionless.dimension,
                SteRadian.dimension,
                AngularMil.dimension
            }
        )
        or dimsys_SI.get_dimensional_dependencies(dimension) == {}
    )
