from typing import ItemsView, KeysView, Protocol, TypeVar, Union, ValuesView, overload
import sympy

from mathpad.val import Q, ValT, Val
from mathpad.vector import Vec, VecT
from mathpad.equation import Equation


@overload
def simplify(obj: ValT) -> ValT:
    ...

@overload
def simplify(obj: Equation) -> Equation:
    ...

@overload
def simplify(obj: VecT) -> VecT:
    ...

def simplify(obj: Union[ValT, Equation, VecT]) -> Union[ValT, Equation, VecT]:
    if isinstance(obj, Equation):
        # TODO: simplification that actually makes use of equality

        return Equation(
            simplify(obj.lhs),
            simplify(obj.rhs)
        )
    
    elif isinstance(obj, Vec):
        return obj.__class__(
            obj.space,
            sympy.simplify(obj.expr) # type: ignore
        )

    else:
        return obj.__class__(
            obj.units,
            sympy.simplify(obj.expr)
        )


@overload
def factor(obj: ValT) -> ValT:
    ...


@overload
def factor(obj: Equation) -> Equation:
    ...


@overload
def factor(obj: VecT) -> VecT:
    ...


def factor(
    obj: Union[ValT, Equation, VecT]
) -> Union[ValT, Equation, VecT]:
    if isinstance(obj, Equation):
        # TODO: simplification that actually makes use of equality
        return Equation(
            factor(obj.lhs),
            factor(obj.rhs)
        )
    
    elif isinstance(obj, Vec):
            
        return obj.__class__(
            obj.space,
            sympy.factor(obj.expr)
        )

    else:
        return obj.__class__(
            obj.units,
            sympy.factor(obj.expr) # type: ignore
        )


@overload
def expand(obj: ValT) -> ValT:
    ...


@overload
def expand(obj: Equation) -> Equation:
    ...


@overload
def expand(obj: VecT) -> VecT:
    ...


def expand(
    obj: Union[ValT, Equation, VecT]
) -> Union[ValT, Equation, VecT]:
    if isinstance(obj, Equation):
        # TODO: simplification that actually makes use of equality
        return Equation(expand(obj.lhs), expand(obj.rhs))

    elif isinstance(obj, Vec):
        return obj.__class__(
            obj.space,
            sympy.expand(obj.expr)
        )

    else:
        return obj.__class__(
            obj.units,
            sympy.expand(obj.expr)
        )


# Until a contravariant Map type is added to typing, we have to use this
# https://github.com/python/typing_extensions/issues/5#issue-1241825018

VecOrVal = TypeVar("VecOrVal", bound=Union[Val, Vec], covariant=True)
VecOrValQ = TypeVar("VecOrValQ", bound=Union[Q[Val], Vec], covariant=True)

class SubstitutionMap(Protocol[VecOrVal, VecOrValQ]):
    def keys(self) -> KeysView[VecOrVal]: ...
    def items(self) -> ItemsView[VecOrVal, VecOrValQ]: ...
    def values(self) -> ValuesView[VecOrValQ]: ...


@overload
def subs(obj: ValT, substitutions: SubstitutionMap) -> ValT:
    ...


@overload
def subs(obj: Equation, substitutions: SubstitutionMap) -> Equation:
    ...

@overload
def subs(obj: VecT, substitutions: SubstitutionMap) -> VecT:
    ...

def subs(
    obj: Union[ValT, Equation, VecT],
    substitutions: SubstitutionMap,
) -> Union[ValT, Equation, VecT]:
    if isinstance(obj, Equation):
        return Equation(
            subs(obj.lhs, substitutions),
            subs(obj.rhs, substitutions),
        )

    else:
        sympy_subsmap = {}

        for from_, to in substitutions.items():
            if not isinstance(to, (Val, Vec)):
                to = from_.__class__(from_.units, to)

            sympy_subsmap[from_.expr] = to.in_units(from_ if isinstance(from_, Val) else from_.space).expr

        return obj.__class__(
            obj.units if isinstance(obj, Val) else obj.space,
            obj.expr.subs(sympy_subsmap) # type: ignore
        )
