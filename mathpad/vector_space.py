from abc import ABC
from typing import (
    TYPE_CHECKING,
    Callable,
    Union,
    Tuple,
    Generic,
    TypeVar,
)
from typing_extensions import Self, TypeVarTuple, Unpack

from sympy import Matrix

from mathpad.dimensions import Angle, Length
from mathpad.val import Dimensionless, Val, Q
from mathpad.units import meter

if TYPE_CHECKING:
    from mathpad.vector import Vec

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
    
    def __init__(self, name: str):
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
            
            assert unit.val == 1, \
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

        assert name in self.base_names, \
            f"{name} is not a base name of {self.__class__}" \
            f" (base names are {self.base_names})"

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
    ) -> 'Vec[Self]':
        """
        Construct a vector of this space from a sequence of values.
        """
        from mathpad.vector import Vec
        return Vec(self, vals) # type: ignore
        
    def __repr__(self) -> str:
        # wrap units in a matrix so it prints nicely
        return repr(Matrix([
            unit.units # type: ignore
            for unit in self.base_units
        ]))
    
    def __str__(self) -> str:
        return f"<{self.name}: {self.__class__.__name__}>"
    
    def __len__(self):
        return len(self.base_names)
    
    def sym(self, name: str):
        from mathpad.vector import Vec
        return Vec(self, name)
    
    @classmethod
    def _get_output_space(
        cls,
        space_a: Union['VectorSpace', Val],
        space_b: Union['VectorSpace', Val],
        op: Callable[[Val, Val], Val],
        name: str
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

    def zeros(self) -> 'Vec[Self]':
        from mathpad.vector import Vec
        return Vec(self, [0] * len(self))
    
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
    
    def __rmul__(self, other: Val) -> 'VectorSpace':
        return VectorSpace._get_output_space(
            other,
            self,
            lambda a, b: a * b,
            self.name
        )

VectorSpaceT = TypeVar("VectorSpaceT", bound=VectorSpace)


class R3(VectorSpace[Length, Length, Length]):
    "R3; euclidean space; [i, j, k] in meters"
    base_units = meter, meter, meter
    base_names = "i", "j", "k"

    

class R2(VectorSpace[Length, Length]):
    "R2; euclidean space; [i, j] in meters"
    base_units = meter, meter
    base_names = "i", "j"

    def from_polar(self, r: Q[Length], theta: Q[Angle]) -> 'Vec[Self]':
        """
        Construct a vector from polar coordinates.
        theta is measured anticlockwise from the +x axis, so you must be careful which value you use.
        For example, if your theta is measured clockwise from the +x axis, use -theta.
        And if your theta is measured clockwise from the y axis, use -theta - pi/2,
        etc
        """
        from mathpad import sin, cos
        return self[
            r * cos(theta),
            r * sin(theta)
        ]
