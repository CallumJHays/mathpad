
from typing import TYPE_CHECKING, Any, Generic, List, Sequence, Tuple, TypeVar
from typing_extensions import Self
import inspect

import sympy
from sympy.physics.vector import vlatex

from mathpad.sympy_extensions import SymbolicMatrixFunction

from mathpad.core.dimensions import Angle, Length
from mathpad.core.val import Q, Val, _extract_deps_from_fn_str, DimensionError
from mathpad.core.vector_space import R2, VectorSpace, VectorSpaceT

if TYPE_CHECKING:
    from mathpad.core.vector import Vector
    # from mathpad.matrix import Matrix, L, R
    
    # HomogeneousTransform = Matrix[VectorSpaceT, VectorSpaceT2]
    

class Frame(Generic[VectorSpaceT]):

    def __init__(
        self,
        space: VectorSpaceT,
        name: str,
        *,
        check: bool = False,
        # wrt: Optional[Tuple[Self, 'HomogeneousTransform[VectorSpaceT]']] = None
    ):
        """
        wrt, if specified, is a tuple of (frame, transform_matrix) where the matrix is the transformation
        """
        self.space = space
        self.name = name
        self.check = check

        # if wrt:
        #     frame, tf = wrt
        #     assert frame.space == space
        #     assert tf.left_frame.space.og_space == space
        #     assert tf.right_frame.space.og_space == space
        #     self.wrt = wrt
        # else:
        #     self.wrt = None
    
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

        if not name in self.space.base_names:
            raise AttributeError(
                f"{name} is not a base name of {self.__class__}" \
                f" (base names are {self.space.base_names})"
            )
            

        res = [0] * len(self)
        res[self.space.base_names.index(name)] = 1
        return self.__getitem__(tuple(res))
    
    def from_polar(
        self: 'Frame[R2]',
        r: Q[Length],
        theta: Q[Angle]
    ) -> 'Vector[R2]':
        """
        Construct a vector from polar coordinates.
        theta is measured anticlockwise from the +x axis, so you must be careful which value you use.
        For example, if your theta is measured clockwise from the +x axis, use -theta.
        And if your theta is measured clockwise from the y axis, use -theta - pi/2,
        etc
        """
        from mathpad.maths.trigonometry import cos, sin
        from mathpad.core.units import meter
        from mathpad.core.vector import Vector

        assert len(self) == 2, f"Can only use from_polar on frames of length 2, not {len(self)}"
        x, y = self.space.base_units
        DimensionError.check(x, y)

        r_ = r if isinstance(r, Val) else Val(meter.units, r) # type: ignore
        return Vector(self, (r_ * cos(theta), r_ * sin(theta)))
    
    def from_complex(
        self: 'Frame[R2]',
        z: Q[Length]
    ) -> 'Vector[R2]':
        """
        Construct a vector from a possibly number or Length
        """

        assert len(self) == 2, f"Can only use from_polar on frames of length 2, not {len(self)}"
        x, y = self.space.base_units
        DimensionError.check(x, y)

        real, imag = z.expr.as_real_imag() if isinstance(z, Val) \
            else (z.real, z.imag) if isinstance(z, complex) \
            else (z, 0) # type: ignore
        return self[real, imag] # type: ignore

    def __getitem__(
        self,
        vals: Tuple[Q[Val], ...]
    ) -> 'Vector[VectorSpaceT]':
        """
        Construct a vector of this frame from a sequence of values.
        """
        from mathpad.core.vector import Vector
        return Vector(self, vals, check=self.check) # type: ignore
        
    # def __repr__(self) -> str:
    #     # wrap units in a matrix so it prints nicely
    #     # TODO: make output optimal for both latex and terminal somehow
    #     return repr(sympy.Matrix([
    #         unit.units # type: ignore
    #         for unit in self.space.base_units
    #     ]))

    def __repr__(self) -> str:
        return f"Frame[{self.space.name}] @ {self.name}"
    

    # def __repr__(self):
    #     return f"Frame({self.space})"
    

    def _repr_latex_(self, wrapped: bool = True):
        
        units_ltx = (
            "\\begin{matrix} "
            + " \\\\ ".join(
                # use vlatex because it applies dot notation where possible
                "\\hat{%s} " % base_name +
                f'\\cdot {vlatex(base_unit.units).replace("- 1.0 ", "-")}' # type: ignore
                for base_name, base_unit in zip(self.space.base_names, self.space.base_units)
            )
            + " \\end{matrix}\\normalsize"
        )

        wrt_ltx = "\\small\\text{wrt. %s}\\normalsize" % self.name if self.name else ""        
        full_ltx = "%s \\hspace{0.7em} %s" % (units_ltx, wrt_ltx)

        return f"$$ {full_ltx} $$" if wrapped else full_ltx
    
    def __str__(self) -> str:
        name_part = f' name="{self.name}"' if self.name else ''
        return f"<{self.space.name}{name_part}>"
    
    def __mul__(self, other: Q[Val]) -> Self:
        return Frame(self.space * other, self.name)
    
    def __rmul__(self, other: Q[Val]) -> Self:
        return Frame(self.space * other, self.name)
    
    
    def __eq__(self, other: 'Frame[VectorSpaceT]') -> bool:
        return self.space == other.space and self.name == other.name
    

    def __rtruediv__(self, other: Val) -> 'Frame[VectorSpaceT]':
        return Frame(other / self.space, self.name)
    
    def __truediv__(self, other: Val) -> 'Frame[VectorSpaceT]':
        return Frame(self.space / other, self.name)
    


    def __rmatmul__(self, repr: str) -> 'Vector[VectorSpaceT]':
        from mathpad.core.vector import Vector

        if "(" in repr:
            # This must be a symbolic function definition.
            # Get the caller frame to find the variables referenced in the string definition
            caller_frame = inspect.currentframe().f_back # type: ignore
            assert caller_frame

            deps = list(_extract_deps_from_fn_str(repr, caller_frame, (sympy.Function, sympy.Symbol)))

            func_name, _depstr = repr.split("(")

            name = r"\vec{" + func_name + "}"

            # construct a symbolic vector as a function of specified dependencies
            expr = SymbolicVectorFunction(
                name,
                len(self),
                1,
                [d.expr for d in deps], # type: ignore
            )
            expr.set_space(self.space) # can't be included in above constructor because its signature can't change
            return Vector(self, expr)

        else:
            return Vector(self,
                sympy.MatrixSymbol("vec{" + repr + "}", len(self.space.base_units), 1)) # type: ignore
        
        
    
    def __len__(self):
        return len(self.space)


class SymbolicVectorFunction(SymbolicMatrixFunction):

    def __new__(cls, name: str, length: int, width: int, function_of: Sequence[sympy.Expr]):
        assert width == 1, "Vector functions are only defined for width=1"
        return super().__new__(cls, name, length, 1, function_of)
    
    def __init__(self, name: str, length: int, width: int, function_of: Sequence[sympy.Expr]):
        super().__init__(name, length, 1, function_of)
        self.space = None

    def set_space(self, space: VectorSpace):
        self.space = space

    def _entry(self, i: int, j: int) -> sympy.Function:
        assert j == 0, "Vector functions are only defined for j=0"
        assert self.space, "Vector function must be set to a space before it can be evaluated"
        orig = super()._entry(i, j)
        base_names = self.space.base_names
        new_name: str = orig.name.split('[')[0] + '_{%s}' % base_names[i] # type: ignore
        return sympy.Function(new_name)(orig.args[0])
        # match = re.match(self.name + r"(?P<brackets>\[(?P<idx>\d+), \d+\])", orig)
        # match.group()
        # return orig



FrameT = TypeVar("FrameT", bound=Frame)