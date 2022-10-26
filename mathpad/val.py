from types import FrameType
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union, TypeVar, overload, Callable
import re
from abc import ABC
from typing_extensions import Self, Literal
import inspect

import sympy
import sympy.physics.units as su
from sympy.physics.units.dimensions import Dimension
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units.unitsystem import UnitSystem
from sympy.physics.vector.printing import vlatex
from sympy.physics.units.util import (
    quantity_simplify,
    convert_to,
)

from mathpad.equation import Equation

# TODO: support numpy arrays
Num = Union[int, float, complex]

# this should be a classmethod, but it isn't
_units2dimensional_expr = UnitSystem.get_default_unit_system().get_dimensional_expr


class Val:
    "An value with a set of units. For example 10 ohms or 20 meters / second**2"


    def __init__(
        self,
        units: Union[su.Quantity, sympy.Expr],  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,
    ):
    
        # clean up the case where you get units**1.0
        if isinstance(units, sympy.Pow) and units.exp == 1:
            units = units.base

        self.expr: sympy.Expr = sympy.sympify(val)
        self.units: su.Quantity = quantity_simplify(sympy.sympify(units))

        units_dimension = _units2dimensional_expr(self.units) # type: ignore

        if hasattr(self, 'dimension'):
            # if a dimension has already been specified by the class, check that it matches

            if _is_dimensionless(units_dimension) and _is_dimensionless(self.dimension):
                # equivalent_dims() doesn't handle this case properly, but this works
                return
            
            assert dimsys_SI.equivalent_dims(units_dimension, self.dimension), (
                f"Units {self.units} do not match the dimensionality of {self.__class__.__name__} ({self.dimension}).\n"
                f"Instead got {units_dimension}"
            )
        
        else:
            # otherwise assign it to the dimensionality of the units provided
            self.dimension = units_dimension

    def __hash__(self):
        return hash(self.expr)

    @overload
    def __eq__(self, other: "Val") -> "Equation":
        ...

    @overload
    def __eq__(self, other: "Q[Self]") -> "Equation":
        ...

    def __eq__(self, other: "Q[Val]") -> "Equation":
        if isinstance(other, Val):
            SumDimensionsMismatchError.check(self, "==", other)
        return Equation(self, other)

    def __req__(self, other: Num) -> "Equation":
        return Equation(other, self)

    def __repr__(self) -> str:
        return self._repr(True)

    # Rich displays; Ipython etc
    def _repr_latex_(self, wrapped: bool = True):
        # use vlatex because it applies dot notation where possible


        expr_str = str(self.expr.evalf())

        # if this has an exponent
        if 'e+' in expr_str:
            # move the decimal place if the exponent is small
            expr, exponent = expr_str.split('e+')
            if int(exponent) < 5:
                idx = expr.index('.')
                expr_str = expr[:idx] + expr[idx+1:idx+1+int(exponent)] + '.' + expr[idx+1+int(exponent):]

        if all(c in "0123456789." for c in expr_str):
            if "." in expr_str:
                # remove trailing zeros for whole numbers
                whole, decimals = expr_str.split(".")
                decimals = decimals.rstrip('0')
                if not any(decimals):
                    expr_ltx = whole
                else:
                    # TODO: global / context managed sigfig settings
                    expr_ltx = f"{whole}.{decimals[:4]}{'..' if len(decimals) > 4 else ''}"
            else:
                expr_ltx = expr_str
        else:
            expr_ltx = vlatex(self.expr)
        
        # remove '1.0's
        clean_expr_ltx = expr_ltx.replace("- 1.0 ", "-")
        units_ltx = "dimensionless" if self.units == 1 else vlatex(self.units)

        spacer_ltx = "\\hspace{1.25em}"

        full_ltx = f"{clean_expr_ltx} {spacer_ltx} {units_ltx}"

        return f"$$ {full_ltx} $$" if wrapped else full_ltx

    def _repr(self, with_units: bool) -> str:
        # ignore 0's following last non-zero decimal
        res = re.sub(
            r"(\d+\.\d*[^0])0+",
            r"\1",
            str(self.expr.evalf(6)),  # type: ignore
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

        # TODO: use superscript for exponents

        return res
    
    def eval(self, sigfigs: int = 6):
        "Return a new Val with consts evaluated to their floating point equivalent with number of sigfigs"
        return self.__class__(self.units, self.expr.evalf(sigfigs))

    def in_units(self, units: Union[Literal["SI"], "Val"]) -> Self:
        """
        Return a new Val with the same value but in the specified units. The expr of the new Val will be rescaled as necessary if units change the scaling factor.

        If units is "SI", convert to the default SI units for this value's dimension.

        If units is a `Val`, attempt to convert to the units of that value. Their underlying dimensionality must be equivalent.

        See also: `.re()` for replacing units rather than converting
        """
        
        if isinstance(units, str):
            assert units == "SI", f"Only 'SI' is supported. Got {units}"
            new_units = UnitSystem.get_unit_system(units)._base_units

        else:
            SumDimensionsMismatchError.check(self, ".in_units", units)
            new_units = units.units

        units_factor, new_units = _split_coeff_and_units(
            convert_to(self.units, new_units)  # type: ignore
        )
        new_val = units_factor * self.expr

        return self.__class__(new_units, new_val)

    def re(self, units: "Val") -> "Val":
        """
        Return a new value with the same value but replaced units.

        Useful for defining functions of other values with numeric literals in place of dimensionally-accurate Vals.

        For example,
        >>> acceleration = (6 * t).re(m/s**2)
        6*t meters/second**2
        >>> voltage = (3 * sqrt(t)).re(V)
        3*t**0.5 volts
        """
        assert units.expr == 1, f"valid units must have an expr == 1. Got {units}"
        return Val(units.units, self.expr)

    def __add__(self, other: "Q[Self]") -> Self:
        return self._sum_op(other, lambda a, b: a + b, "+", False)

    def __radd__(self, other: Num) -> Self:
        return self._sum_op(other, lambda a, b: b + a, "+", True)

    def __sub__(self, other: "Q[Self]") -> Self:
        return self._sum_op(other, lambda a, b: a - b, "-", False)

    def __rsub__(self, other: Num) -> Self:
        return self._sum_op(other, lambda a, b: b - a, "-", True)

    def __neg__(self):
        return self.__class__(self.units, -self.expr) # type: ignore

    def __mul__(self, other: "Q[Val]") -> "Val":
        return self._prod_op(other, lambda a, b: a * b, is_pow=False)

    def __rmul__(self, other: Union[Num, str]) -> Self:

        if isinstance(other, str):
            assert self.expr == 1, "Attempted to create variable with a non-unit Val"

            # TODO: support variables which are functions of a symbol other than t. should this be a fn() fn?
            if "(" in other:

                caller_frame = inspect.currentframe().f_back # type: ignore
                assert caller_frame
                sym = _sym_func(other, caller_frame)

            else:
                sym = sympy.Symbol(other)

            return self.__class__(self.units, sym)

        else:
            return self._prod_op(other, lambda a, b: b * a, is_pow=False)


    def __truediv__(self, other: "Q[Val]") -> "Val":
        return self._prod_op(other, lambda a, b: a / b, is_pow=False)

    def __rtruediv__(self, other: Num) -> "Val":
        return self._prod_op(other, lambda a, b: b / a, is_pow=False)

    def __pow__(self, other: "Q[Val]") -> "Val":
        from mathpad.vector_space import VectorSpace
        from mathpad.vector import Vector
        from mathpad.matrix import Matrix

        # exponents should always be dimensionless
        if isinstance(other, Val) and not _is_dimensionless(other.dimension):
            raise DimensionalExponentError(
                f"Exponents must always be dimensionless. Instead got {other.dimension}: {other}"
            )
        
        other_expr = other.expr if isinstance(other, Val) else other

        new_expr = self.expr if other_expr == 1 else self.expr ** other_expr
        new_units = self.units ** other_expr

        new_dims = _units2dimensional_expr(new_units)
        dimension_unchanged = dimsys_SI.equivalent_dims(
            self.dimension, new_dims
        )

        if dimension_unchanged:
            res = self.__class__(new_units, new_expr) # type: ignore

        elif new_units == Dimensionless.base_units:
            res = Dimensionless(new_units, new_expr)  # type: ignore

        else:
            # TODO: a big lookup table for dimensional expr -> Val subclass
            res = Val(new_units, new_expr)  # type: ignore

        return res

    def __rpow__(self, other: Num) -> "Dimensionless":
        if not _is_dimensionless(self.dimension):
            raise DimensionalExponentError(
                f"Exponents must always be dimensionless. Instead got {self.dimension}: {self}"
            )
        
        return Dimensionless(1, other ** self.expr)

    def _sum_op(
        self,
        other: "Q[Self]",
        op: Callable[[Any, Any], Any],
        op_str: str,
        reverse: bool,
    ) -> Self:
        from mathpad.vector import Vector

        assert not isinstance(other, Vector)

        other_units, other_val = (
            (other.units, other.expr) if isinstance(other, Val) else (self.units, other)
        )

        if isinstance(other, Val):
            SumDimensionsMismatchError.check(
                other if reverse else self, op_str, self if reverse else other
            )

        other_units_rescale_factor = quantity_simplify(
            convert_to(other_units, self.units) / self.units
        )

        # choose the larger of the two input units as the output units
        use_other_units = other_units_rescale_factor > 1
        new_units = other_units if use_other_units else self.units

        self_val_rescaled = (
            self.expr / other_units_rescale_factor if use_other_units else self.expr
        )
        other_val_rescaled = (
            other_val if use_other_units else other_val * other_units_rescale_factor
        )

        new_val = op(self_val_rescaled, other_val_rescaled)

        res = self.__class__(new_units, new_val)

        return res # type: ignore

    def _prod_op(
        self,
        other: "Q[Val]",
        op: Callable[[Any, Any], Any],
        is_pow: bool,
    ) -> "Val":
        from mathpad.vector_space import VectorSpace
        from mathpad.vector import Vector
        from mathpad.matrix import Vector, Matrix

        if isinstance(other, (Vector, VectorSpace, Matrix)):
            # let the Vector/VectorSpace obj handle the multiplication by returning NotImplemented
            return NotImplemented

        other_units, other_val = (
            (other.units, other.expr)
            if isinstance(other, Val)
            else (other if is_pow else 1, other)
        )

        rescale_factor, new_units = _split_coeff_and_units(op(self.units, other_units))

        new_val = rescale_factor * op(self.expr, other_val)
        if isinstance(new_val, sympy.Expr):
            new_val = quantity_simplify(new_val)

        # _units2dimensional_expr doesn't handle exponent radians properly. Do it manually here:
        if isinstance(new_units, sympy.Pow):
            new_exp = quantity_simplify(new_units.exp.subs({ su.radian: 1})) # type: ignore
            new_units = new_units.base ** new_exp

        new_dims = _units2dimensional_expr(new_units)
            
        dimension_unchanged = dimsys_SI.equivalent_dims(
            self.dimension, new_dims
        )

        if dimension_unchanged:
            res = self.__class__(new_units, new_val) # type: ignore

        elif new_units == Dimensionless.base_units:
            res = Dimensionless(new_units, new_val)  # type: ignore

        else:
            # TODO: a big lookup table for dimensional expr -> Val subclass
            res = Val(new_units, new_val)  # type: ignore

        return res


ValT = TypeVar("ValT", bound=Val)
Q = Union[ValT, Num, Val]
"Any Val, specific or not - or a number"
X = Union[ValT, Val]
"Any Val, specific or not - but not a number"


class DimensionError(TypeError):
    
    @classmethod
    def check(cls, a: Val, b: Val):
        
        if _is_dimensionless(a.dimension) and _is_dimensionless(b.dimension):
            # equivalent_dims() doesn't handle this case properly
            return

        if not dimsys_SI.equivalent_dims(a.dimension, b.dimension):
            a_dim_str = a.dimension.name if isinstance(a.dimension, Dimension) else str(a.dimension)
            b_dim_str = b.dimension.name if isinstance(b.dimension, Dimension) else str(b.dimension)
            raise cls(f"Dimension mismatch: {a_dim_str} != {b_dim_str}")


class DimensionalExponentError(DimensionError):
    
    @classmethod
    def check(cls, exponent: Val):
        if not _is_dimensionless(exponent.dimension):
            raise cls(f"Exponent must be dimensionless: {exponent.dimension}")


class SumDimensionsMismatchError(DimensionError):
    def __init__(
        self,
        left: Val,
        operation: str,
        right: Val,
        extra_msg: str = "",
    ):
        self.args = (
            f'{extra_msg}[{left.dimension}: {left}] "{operation}" [{right.dimension}: {right}]',
        )

    @classmethod
    def check(cls, a: Val, op_str: str, b: Val):
        try:
            DimensionError.check(a, b)
        except DimensionError:
            raise cls(a, op_str, b)


def _split_coeff_and_units(unit_expr: sympy.Expr) -> Tuple[float, Any]:
    # TODO: test and refactor
    converted = quantity_simplify(unit_expr)  # type: ignore
    if converted.is_Number:
        return converted, Dimensionless.base_units  # type: ignore

    try:
        units_factor = converted.args[0]
        if units_factor.is_Number:
            return units_factor, quantity_simplify(unit_expr / units_factor)

    except AttributeError:
        pass

    return 1, unit_expr


class Unit(Val):

    dimension: Union[su.Dimension, sympy.Expr]
    base_units: Union[su.Quantity, sympy.Expr]
    
    def __init_subclass__(cls):
        # ensure that subclasses specify a dimension
        assert hasattr(cls, "dimension"), f"{cls} must specify dimension"
        assert hasattr(cls, "base_units"), f"{cls} must specify base_units"
        return super().__init_subclass__()


class Dimensionless(Unit):

    dimension = su.Dimension(1)  # type: ignore
    base_units = sympy.sympify(1)

    def __init__(
        self,
        units: Union[su.Quantity, sympy.Expr, Literal[1]],  # may also be a sympy expression of su.Quantities, ie su.meter**2
        val: Union[sympy.Expr, Num] = 1,  # gets set in __init__
    ):
        # measures of angle are technically dimensionless
        assert _is_dimensionless(_units2dimensional_expr(units))
        super().__init__(units, val) # type: ignore

def _is_dimensionless(dimension):
    from mathpad.dimensions import Angle, AngularMil, SteRadian

    # accepts output of units2dimensional_expr (an expression, not a dimension object); so normalize here
    if isinstance(dimension, Dimension):
        dimension = dimension.args[0]

    return (
        dimension in [
            1,
            None,
            Angle.dimension.args[0],
            Dimensionless.dimension.args[0],
            SteRadian.dimension.args[0],
            AngularMil.dimension.args[0],
        ]
        or dimsys_SI.get_dimensional_dependencies(dimension) == {}
    )

def _sym_func(text: str, caller_frame: FrameType) -> sympy.Expr:
    assert (
        text.count("(") == 1 and text.count(")") == 1 and text[-1] == ")"
    ), f"Malformed variable name. Variables which are functions of symbols must take the form 'f(x[, y, ...])'. Insted got {other}"

    function_name, depstr = text.split("(")
    deps = [x.strip() for x in depstr[:-1].split(",")]

    caller_vars = {**caller_frame.f_locals, **caller_frame.f_globals}
    dep_syms = []
    for dep in deps:

        val: Optional[Val] = caller_vars.get(dep, None)
        assert val, f"Symbolic Function {text} depends on unknown symbol {dep}. " \
            "Please ensure a variable with this name is defined in the caller's scope."
        
        assert isinstance(val.expr, (sympy.Symbol, sympy.Function)), \
            f"Variable {text} depends on non-symbolic Val '{val}'. \n" \
            f"Expected {dep}.expr to be a sympy.Symbol, but got {val.expr} ({type(val.expr)})."
        
        dep_syms.append(val.expr)
        
    sym = sympy.Function(function_name)(*dep_syms) # type: ignore
    return sym