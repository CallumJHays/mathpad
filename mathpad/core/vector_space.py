from typing import (
    TYPE_CHECKING,
    Callable,
    Optional,
    Union,
    Tuple,
    Generic,
    TypeVar,
    Type
)
import inspect
from typing_extensions import Self, TypeVarTuple, Unpack

import sympy
from sympy import MatrixSymbol
from sympy.physics.vector import vlatex

from mathpad.sympy_extensions.SymbolicMatrixFunction import SymbolicMatrixFunction

from mathpad.core.dimensions import Angle, Length
from mathpad.core.val import Dimensionless, Val, Q, _extract_deps_from_fn_str
from mathpad.core.common_vals import dimensionless

if TYPE_CHECKING:
    from mathpad.core.vector import Vector
    from mathpad.core.frame import Frame

BaseUnits = TypeVarTuple('BaseUnits') # ideally bound=Val

class VectorSpace(Generic[Unpack[BaseUnits]]):
    """
    A VectorSpace is a ordered set of fields, each of which has a dimension type.

    Example: R3 is a VectorSpace of 3 fields {x, y, z}, each of which has a dimension of Length.

    Cannot be used directly; must be subclassed first.

    """
    
    # # these must be specified by subclasses, or by a direct instantiation of VectorSpace
    base_units: Tuple[Unpack[BaseUnits]] # must be a tuple of Val
    base_names: Tuple[str, ...]
    name: str
    
    def __init_subclass__(cls) -> None:
        # TODO: is this really necessary?
        if cls.__qualname__ == "Homogeneous":
            return
        
        assert hasattr(cls, "base_units"), \
            f"VectorSpace subclass {cls.__qualname__} must specify base_units"
        assert isinstance(cls.base_units, tuple) \
            and all(isinstance(u, Val) for u in cls.base_units), \
            f"base_units must be a tuple of Val. Instead got {cls.base_units}"
        
        assert hasattr(cls, "base_names"), \
            f"VectorSpace subclass {cls.__qualname__} must specify base_names"
        assert isinstance(cls.base_names, tuple) \
            and all(isinstance(n, str) for n in cls.base_names), \
            f"base_names must be a tuple of str. Instead got {cls.base_names}"
        
        assert len(cls.base_units) == len(cls.base_names), \
            f"base_units and base_names must be the same length. Instead got {cls.base_units} and {cls.base_names}"

    # override __new__ to allow for a hacky syntax with nice type inference:
    # `O: Frame[R3] = R3("O")` instead of
    # `O: Frame[VectorSpace[Length, Length, Length]] = R3("O")`
    def __new__(cls, name: str, check: bool = False) -> 'Frame[Self]':
        from mathpad.core.frame import Frame
        # this may be the hackiest thing I've ever done
        space = super().__new__(cls)
        space.name = cls.__name__
        return Frame(space, name, check=check)

    @classmethod    
    def new(cls, name: str, base_names: Tuple[str, ...], base_units: Tuple[Unpack[BaseUnits]]) -> 'VectorSpace[Unpack[BaseUnits]]':
        assert len(set(base_names)) == len(base_names), \
            f"base_names must be unique. Instead got {base_names}"
        assert len(base_names) == len(base_units), \
            f"base_names and base_units must be the same length. Instead got {base_names} and {base_units}"
        
        space = super().__new__(cls)
        space.name = name
        space.base_names = base_names
        space.base_units = base_units

        return space

    def _repr_latex_(self, wrapped: bool = True):
        
        units_ltx = (
            "\\begin{matrix} "
            + " \\\\ ".join(
                # use vlatex because it applies dot notation where possible
                "\\hat{%s} " % base_name +
                f'\\cdot {vlatex(base_unit.units).replace("- 1.0 ", "-")}' # type: ignore
                for base_name, base_unit in zip(self.base_names, self.base_units)
            )
            + " \\end{matrix}\\normalsize"
        )

        wrt_ltx = "\\small\\text{wrt. %s}\\normalsize" % self.name if self.name else ""        
        full_ltx = "%s \\hspace{0.7em} %s" % (units_ltx, wrt_ltx)

        return f"$$ {full_ltx} $$" if wrapped else full_ltx
    
    
    def __call__(self, name: str) -> 'Frame[Self]':
        from mathpad.core.frame import Frame
        return Frame(self, name)

    @classmethod
    def _get_output_space(
        cls,
        space_a: Union[Self, Val],
        space_b: Union[Self, Val],
        op: Callable[[Val, Val], Val],
        name: str
    ) -> Self:
        """
        Like Val, multiplicative operations result in unknown dimensionality for the type-checker.
        unlike Val, we need to create an output vector space with the resulting base_units
        first, before we can create the output vector.
        """

        assert isinstance(space_a, VectorSpace) or isinstance(space_b, VectorSpace)

        a_units = space_a.base_units if isinstance(space_a, VectorSpace) else [Val(space_a.units, 1)] * len(space_b) # type: ignore
        b_units = space_b.base_units if isinstance(space_b, VectorSpace) else [Val(space_b.units, 1)] * len(space_a) # type: ignore

        return VectorSpace.new(
            name,
            space_b.base_names if isinstance(space_b, VectorSpace) else space_a.base_names,
            tuple(op(a, b) for a, b in zip(a_units, b_units))
        )
    
    def __truediv__(self, other: Val) -> Self:
        return VectorSpace._get_output_space(
            self,
            other,
            lambda a, b: a / b,
            self.name
        )
    
    def __rtruediv__(self, other: Val) -> Self:
        return VectorSpace._get_output_space(
            other,
            self,
            lambda a, b: a / b,
            self.name
        )
    
    def __mul__(self, other: Val) -> Self:
        return VectorSpace._get_output_space(
            self,
            other,
            lambda a, b: a * b,
            self.name
        )

    def __rmul__(self, other: Val) -> Self:
        return self._get_output_space(
            other,
            self,
            lambda a, b: a * b,
            self.name
        )
    
    def __eq__(self, other: Self) -> bool:
        return self.name == other.name \
            and self.base_units == other.base_units \
            and self.base_names == other.base_names
    
    def __len__(self) -> int:
        return len(self.base_units)
    
    def homogeneous(self, name: Optional[str] = None) -> 'Homogeneous[Self]':
        return Homogeneous(self, name)
    

VectorSpaceT = TypeVar("VectorSpaceT", bound=VectorSpace, covariant=True) # type: ignore [reportMissingTypeArguments]

class Homogeneous(VectorSpace[Unpack[BaseUnits], Dimensionless], Generic[VectorSpaceT, Unpack[BaseUnits]]):
    """
    A vector space projected to a homogeneous space by postfixing a dimensionless unit.
    Homogeneous[VectorSpace[i, j, k]] = VectorSpace[i, j, k, w]
    """


    def __init__(self, space: VectorSpaceT, name: Optional[str] = None):

        base_units: Tuple[Unpack[BaseUnits], Dimensionless] \
            = (*space.base_units, Dimensionless(1, 1)) # type: ignore [assignment]
            
        super().__init__(
            name or f"Homogeneous[{space.name}]",
            (*space.base_names, "w"),
            base_units
        )
        self.og_space = space

class R3(VectorSpace[Dimensionless, Dimensionless, Dimensionless]):
    "R3; euclidean space; dimensionless [i, j, k]`"
    base_units = dimensionless, dimensionless, dimensionless
    base_names = "i", "j", "k"

class R2(VectorSpace[Dimensionless, Dimensionless]):
    "R2; euclidean space; dimensionless [i, j]"
    base_units = dimensionless, dimensionless
    base_names = "i", "j"
