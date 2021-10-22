from typing import Any, Tuple, Type, Union, TypeVar, overload, Callable
import re
from abc import ABC

import sympy
import sympy.physics.units as su
from sympy.physics.units.dimensions import Dimension
from sympy.physics.units.quantities import Quantity
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units.unitsystem import UnitSystem
from sympy.physics.vector import dynamicsymbols
from sympy.physics.vector.printing import vlatex
from sympy.physics.units.util import (
    quantity_simplify,
    convert_to,
)

from mathpad.equation import Equation
from mathpad.global_options import _global_options

# TODO: support numpy arrays
Num = Union[int, float, complex]
_UNSET = ()

# this should be a classmethod, but it isn't
_units2dimensional_expr = UnitSystem.get_default_unit_system().get_dimensional_expr


class AbstractPhysicalQuantity(ABC):
    "An object representing a physical quantity. For example 10 ohms or 20 meters / second**2"

    dimension: su.Dimension = _UNSET  # type: ignore

    def __new__(
        cls,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,  # gets set in __init__
    ):
        return super().__new__(cls)

    def __init_subclass__(cls):
        assert (
            str(cls) == "<class 'mathpad.physical_quantity.Unit'>"
            or cls.dimension is not _UNSET
        )
        super().__init_subclass__()
    
    def new(self: "GPhysicalQuantity", val: sympy.Expr, units: sympy.Expr = None) -> "GPhysicalQuantity":
        "Creates a new AbstractPhysicalQuantity of the same class. if units == None; units = self.units"
        if units == None:
            units = self.units
        return self.__class__(units, val)

    def __init__(
        self,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,
    ):

        self.val: sympy.Symbol = sympy.sympify(val)
        self.units: su.Quantity = quantity_simplify(sympy.sympify(units))

        assert self.dimension is not _UNSET
        units_dimension = _units2dimensional_expr(self.units)

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

    # Rich displays; Ipython etc
    def _repr_latex_(self):
        # use vlatex because it applies dot notation where possible
        val_ltx = vlatex(self.val)
        clean_val_ltx = val_ltx.replace("- 1.0 ", "-")
        units_ltx = "dimensionless" if self.units == 1 else vlatex(self.units)

        spacer_ltx = "\\hspace{1.25em}"
        # remove '1.0's

        return f"$\\displaystyle {clean_val_ltx} {spacer_ltx} {units_ltx}$"

    def _repr_png_(self):
        return self.val._repr_png_()

    def _repr_svg_(self):
        return self.val._repr_svg_()

    def _repr_disabled(self):
        return self.val._repr_disabled()

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

        # replace "Derivative" and "Integral" with their input equivalents

        # TODO: Make derivatives and integrals easier to read
        # res = res.replace("Derivative", "ᵈ⁄dt").replace("Integral", "∫")

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
        self: "GPhysicalQuantity", units: Union[str, "AbstractPhysicalQuantity"]
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

        return self.new(new_val, new_units)

    @overload
    def __add__(self, other: "PhysicalQuantity") -> "PhysicalQuantity":
        ...

    @overload
    def __add__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    @overload
    def __add__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    @overload
    def __add__(
        self: "GPhysicalQuantity", other: "GPhysicalQuantity"
    ) -> "GPhysicalQuantity":
        ...

    def __add__(self, other: "Q[GPhysicalQuantity]"):
        return self._sum_op(other, lambda a, b: a + b, "+", False)

    def __radd__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        return self._sum_op(other, lambda a, b: b + a, "+", True)

    @overload
    def __sub__(
        self: "GPhysicalQuantity", other: "PhysicalQuantity"
    ) -> "GPhysicalQuantity":
        ...

    @overload
    def __sub__(self, other: "GPhysicalQuantity") -> "GPhysicalQuantity":
        ...

    @overload
    def __sub__(self: "GPhysicalQuantity", other: Num) -> "GPhysicalQuantity":
        ...

    @overload
    def __sub__(
        self: "GPhysicalQuantity", other: "GPhysicalQuantity"
    ) -> "GPhysicalQuantity":
        ...

    def __sub__(self, other: "Q[GPhysicalQuantity]"):
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

    def __rmul__(
        self: "GPhysicalQuantity", other: Union[Num, str]
    ) -> "GPhysicalQuantity":

        if isinstance(other, str):
            assert (
                self.val == 1
            ), "Attempted to create variable with a non-unit AbstractPhysicalQuantity"

            # TODO: support variables which are functions of a symbol other than t. should this be a fn() fn?
            if "(" in other:
                assert (
                    other.count("(") == 1 and other.count(")") == 1 and other[-1] == ")"
                ), f"Malformed variable name. Variables which are functions of symbols must take the form 'f(x)'. Insted got {other}"

                function_name, the_rest = other.split("(")
                function_of = [x.strip() for x in the_rest[:-1].split(",")]
                if len(function_of) == 1 and function_of[0] == "t":
                    sym = dynamicsymbols(function_name)

                else:
                    # TODO: test this
                    sym = sympy.Function(function_name)(function_of)
            else:
                sym = sympy.Symbol(other)

            return self.new(sym)

        else:
            return self._prod_op(other, lambda a, b: b * a, is_pow=False)

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
                f"Exponents must always be dimensionless. Instead got {other.dimension}: {other}"
            )
        return self._prod_op(other, lambda a, b: a ** b, is_pow=True)

    __xor__ = __pow__

    def __rpow__(self, other: Num) -> "Dimensionless":
        if not _is_dimensionless(self.dimension):
            raise DimensionalExponentError(
                f"Exponents must always be dimensionless. Instead got {self.dimension}: {self}"
            )
        res = self._prod_op(other, lambda a, b: b ** a, is_pow=True)
        assert isinstance(res, Dimensionless)
        return res

    __rxor__ = __pow__

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

        other_units_rescale_factor = quantity_simplify(
            convert_to(other_units, self.units) / self.units
        )

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

        res = self.new(new_val, new_units)

        if _global_options.auto_simplify:
            from mathpad.algebra import simplify

            return simplify(res)

        else:
            return res

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
            self.dimension, _units2dimensional_expr(new_units)
        )

        if dimension_unchanged:
            res = self.new(new_val, new_units)

        elif new_units == Dimensionless.default_units:
            res = Dimensionless(new_units, new_val)  # type: ignore

        else:
            # TODO: a big lookup table for dimensional expr -> AbstractPhysicalQuantity subclass
            res = PhysicalQuantity(new_units, new_val)  # type: ignore

        if _global_options.auto_simplify:
            from mathpad.algebra import simplify

            return simplify(res)

        else:
            return res


GPhysicalQuantity = TypeVar("GPhysicalQuantity", bound=AbstractPhysicalQuantity)
Q = Union[GPhysicalQuantity, Num, "PhysicalQuantity"]


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
        if not dimsys_SI.equivalent_dims(a.dimension, b.dimension) and \
                not (_is_dimensionless(a.dimension) and _is_dimensionless(b.dimension)):
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


class Unit(AbstractPhysicalQuantity):
    pass


class Dimensionless(Unit):

    dimension = su.Dimension(1)  # type: ignore
    default_units = sympy.sympify(1)

    def __new__(
        cls,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,  # gets set in __init__
    ):
        # measures of angle are technically dimensionless
        assert _is_dimensionless(_units2dimensional_expr(units))
        self = super().__new__(cls, units, val)
        return self


class PhysicalQuantity(AbstractPhysicalQuantity):
    """A physical quantity whose dimensionality cannot be type-hinted, but will still check at runtime."""

    dimension = None  # type: ignore # gets set in __init__

    def __new__(
        cls,
        units: su.Quantity,  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,  # gets set in __init__
    ):
        dimension = _units2dimensional_expr(units)

        # catch the case when a quantity is dimensionless (ie 1 meter/meter) -
        # class as Dimensionless for
        if _is_dimensionless(dimension):
            res = Dimensionless(units, val)

        else:
            res = super().__new__(cls, units, val)
            res.dimension = dimension  # type: ignore

        return res


def _is_dimensionless(dimension):
    from mathpad.physical_quantities import Angle, AngularMil, SteRadian

    # accepts output of units2dimensional_expr (an expression, not a dimension object); so normalize here
    if isinstance(dimension, Dimension):
        dimension = dimension.args[0]

    return (
        any(
            dimension == dim
            for dim in [
                1,
                Angle.dimension.args[0],
                Dimensionless.dimension.args[0],
                SteRadian.dimension.args[0],
                AngularMil.dimension.args[0],
            ]
        )
        or dimsys_SI.get_dimensional_dependencies(dimension) == {}
    )
