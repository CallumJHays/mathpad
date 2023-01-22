from abc import ABC
from typing import (
    TYPE_CHECKING,
    Callable,
    Optional,
    Union,
    Tuple,
    Generic,
    TypeVar
)
import inspect
from typing_extensions import Self, TypeVarTuple, Unpack

import sympy
from sympy import MatrixSymbol
from sympy.physics.vector import vlatex

from mathpad.dimensions import Angle, Length
from mathpad.val import Val, Q, _extract_deps_from_fn_str
from mathpad.units import meter

from mathpad.SymbolicMatrixFunction import SymbolicMatrixFunction

if TYPE_CHECKING:
    from mathpad.vector import Vector

BaseUnits = TypeVarTuple('BaseUnits')

class VectorSpace(Generic[Unpack[BaseUnits]], ABC):
    """
    A VectorSpace is a ordered set of fields, each of which has a dimension.

    Cannot be used directly; must be subclassed first.
    
    VectorSpaces are used to generate vectors, which are members of the space.
    """

    # these must be specified by subclasses
    base_units: Tuple[Unpack[BaseUnits]] # must be a tuple of Val
    base_names: Tuple[str, ...]
    
    def __init__(self, name: Optional[str] = None):
        self.name = name
        # TODO: valid latex name check
        assert self.__class__ is not VectorSpace, \
            "VectorSpace cannot be used directly; must be subclassed first."
    
    def __init_subclass__(cls):
        assert hasattr(cls, 'base_units') and hasattr(cls, 'base_names'), \
            "Vector subclasses must define base_units and base_names"
        assert len(cls.base_names) == len(cls.base_units), \
            "base_names and base_units must have the same length"
        for unit in cls.base_units:
            assert isinstance(unit, Val), \
                f"Base units of {cls.__name__} must be instances of Val, got {unit}"
            
            assert unit.expr == 1, \
                f"Base units of {cls.__name__} must have a value of 1, got {unit}"

    def __getattr__(self, name: str):
        """
        Construct a vector from a base name, with a value of 1 in the direction of the base.

        For example, the R3 VectorSpace has the names: ('i', 'j', 'k').
        Resulting in the following behavior:

        >>> VectorSpace.i == VectorSpace(1, 0, 0)
        True

        >>> VectorSpace.j == VectorSpace(0, 1, 0)
        True

        etc.

        """

        if not name in self.base_names:
            raise AttributeError(
                f"{name} is not a base name of {self.__class__}" \
                f" (base names are {self.base_names})"
            )
            

        res = [0] * len(self)
        res[self.base_names.index(name)] = 1
        return self.__getitem__(tuple(res))

    
    def __getitem__(
        self,
        vals: Union[
            # TODO: Fix up once type mapping lands (to get (eg.) Q[Unit] for Unit in BaseUnits)
            Tuple[Unpack[BaseUnits]], # for when the baseunits are known
            Tuple[Q[Val], ...] # otherwise
        ]
    ) -> 'Vector[Self]':
        """
        Construct a vector of this space from a sequence of values.
        """
        from mathpad.vector import Vector
        return Vector(self, vals) # type: ignore
        
    def __repr__(self) -> str:
        # wrap units in a matrix so it prints nicely
        # TODO: make output optimal for both latex and terminal somehow
        return repr(sympy.Matrix([
            unit.units # type: ignore
            for unit in self.base_units
        ]))
    
    def __eq__(self, other: 'VectorSpace') -> bool:
        return self.name == other.name \
            and self.base_units == other.base_units \
            and self.base_names == other.base_names
    
    def __str__(self) -> str:
        name_bit = f' name="{self.name}"' if self.name else ''
        return f"<{self.__class__.__name__}{name_bit}>"
    
    def __len__(self):
        return len(self.base_names)
    
    def _repr_latex_(self, wrapped: bool = True):
        
        units_ltx = (
            "\\begin{matrix} "
            + " \\\\ ".join(
                # use vlatex because it applies dot notation where possible
                "\hat{%s} " % base_name +
                f'\cdot {vlatex(base_unit.units).replace("- 1.0 ", "-")}' # type: ignore
                for base_name, base_unit in zip(self.base_names, self.base_units)
            )
            + " \\end{matrix}\\normalsize"
        )

        wrt_ltx = "\\small\\text{wrt. %s}\\normalsize" % self.name if self.name else ""        
        full_ltx = "%s \\hspace{0.7em} %s" % (units_ltx, wrt_ltx)

        return f"$$ {full_ltx} $$" if wrapped else full_ltx

    @classmethod
    def _get_output_space(
        cls,
        space_a: Union['VectorSpace', Val],
        space_b: Union['VectorSpace', Val],
        op: Callable[[Val, Val], Val],
        name: Optional[str]
    ) -> 'VectorSpace':

        assert isinstance(space_a, VectorSpace) or isinstance(space_b, VectorSpace)

        a_units = space_a.base_units if isinstance(space_a, VectorSpace) else [Val(space_a.units, 1)] * len(space_b) # type: ignore
        b_units = space_b.base_units if isinstance(space_b, VectorSpace) else [Val(space_b.units, 1)] * len(space_a) # type: ignore

        # Like Val, multiplicative operations result in unknown dimensionality for the type-checker.
        # unlike Val, we need to create an output vector space with the resulting base_units
        # first, before we can create the output vector.
        class OutputSpace(VectorSpace):
            # keep the same names, so that IJK, etc is preserved. 
            base_names = space_b.base_names if isinstance(space_b, VectorSpace) else space_a.base_names # type: ignore
            base_units = tuple(
                op(a, b) for a, b in zip(a_units, b_units)
            )

        return OutputSpace(name)

    def zeros(self) -> 'Vector[Self]':
        from mathpad.vector import Vector
        return Vector(self, [0] * len(self))
    
    def __truediv__(self, other: Val) -> 'VectorSpace':
        return VectorSpace._get_output_space(
            self,
            other,
            lambda a, b: a / b,
            self.name
        )
    
    def __rtruediv__(self, other: Val) -> 'VectorSpace':
        return VectorSpace._get_output_space(
            other,
            self,
            lambda a, b: a / b,
            self.name
        )
    
    def __mul__(self, other: Val) -> 'VectorSpace':
        return VectorSpace._get_output_space(
            self,
            other,
            lambda a, b: a * b,
            self.name
        )

    def __rmul__(self, other: Val) -> Union['VectorSpace', 'Vector[Self]']:
        return self._get_output_space(
            other,
            self,
            lambda a, b: a * b,
            self.name
        )


    def __rmatmul__(self, repr: str) -> 'Vector[Self]':
        from mathpad.vector import Vector

        if "(" in repr:
            # This must be a symbolic function definition.
            # Get the caller frame to find the variables referenced in the string definition
            caller_frame = inspect.currentframe().f_back # type: ignore
            assert caller_frame

            deps = list(_extract_deps_from_fn_str(repr, caller_frame, (sympy.Function, sympy.Symbol)))

            func_name, _depstr = repr.split("(")

            name = "\\vec{" + func_name + "}"

            # construct a symbolic vector as a function of specified dependencies
            expr = SymbolicMatrixFunction(name, len(self.base_units), 1,
                [d.expr for d in deps])  # type: ignore
            # expr: MatrixExpr = MatrixExpr(_sym_func(sym, caller_frame))
            return Vector(self, expr)

        else:
            return Vector(self,
                MatrixSymbol("\\vec{" + repr + "}", len(self.base_units), 1)) # type: ignore



VectorSpaceT = TypeVar("VectorSpaceT", bound=VectorSpace)


class R3(VectorSpace[Length, Length, Length]):
    "R3; euclidean space; [i, j, k] in meters"
    base_units = meter, meter, meter
    base_names = "i", "j", "k"

    

class R2(VectorSpace[Length, Length]):
    "R2; euclidean space; [i, j] in meters"
    base_units = meter, meter
    base_names = "i", "j"

    def from_polar(self, r: Q[Length], theta: Q[Angle]) -> 'Vector[Self]':
        """
        Construct a vector from polar coordinates.
        theta is measured anticlockwise from the +x axis, so you must be careful which value you use.
        For example, if your theta is measured clockwise from the +x axis, use -theta.
        And if your theta is measured clockwise from the y axis, use -theta - pi/2,
        etc
        """
        from mathpad import sin, cos

        r_ = r if isinstance(r, Val) else Val(meter.units, r) # type: ignore

        return self[
            r_ * cos(theta),
            r_ * sin(theta)
        ]

    def from_complex(self, z: Q[Length]) -> 'Vector[Self]':
        """
        Construct a vector from a possibly number or Length
        """
        real, imag = z.expr.as_real_imag() if isinstance(z, Val) \
            else (z.real, z.imag) if isinstance(z, complex) \
            else (z, 0) # type: ignore
        return self[real, imag] # type: ignore