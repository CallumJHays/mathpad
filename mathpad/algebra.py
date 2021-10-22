from typing import Union, overload, Dict
import sympy

from mathpad.physical_quantity import GPhysicalQuantity, AbstractPhysicalQuantity, Q
from mathpad.equation import Equation


@overload
def simplify(expr_or_eqn: GPhysicalQuantity) -> GPhysicalQuantity:
    ...


@overload
def simplify(expr_or_eqn: Equation) -> Equation:
    ...


def simplify(
    expr_or_eqn: Union[GPhysicalQuantity, Equation]
) -> Union[GPhysicalQuantity, Equation]:
    if isinstance(expr_or_eqn, Equation):
        # TODO: simplification that actually makes use of equality
        return Equation(simplify(expr_or_eqn.lhs), simplify(expr_or_eqn.rhs))

    else:
        return expr_or_eqn.new(sympy.simplify(expr_or_eqn.val))


@overload
def factor(expr_or_eqn: GPhysicalQuantity) -> GPhysicalQuantity:
    ...


@overload
def factor(expr_or_eqn: Equation) -> Equation:
    ...


def factor(
    expr_or_eqn: Union[GPhysicalQuantity, Equation]
) -> Union[GPhysicalQuantity, Equation]:
    if isinstance(expr_or_eqn, Equation):
        # TODO: simplification that actually makes use of equality
        return Equation(factor(expr_or_eqn.lhs), factor(expr_or_eqn.rhs))

    else:
        return expr_or_eqn.new(sympy.factor(expr_or_eqn.val))


@overload
def expand(expr_or_eqn: GPhysicalQuantity) -> GPhysicalQuantity:
    ...


@overload
def expand(expr_or_eqn: Equation) -> Equation:
    ...


def expand(
    expr_or_eqn: Union[GPhysicalQuantity, Equation]
) -> Union[GPhysicalQuantity, Equation]:
    if isinstance(expr_or_eqn, Equation):
        # TODO: simplification that actually makes use of equality
        return Equation(expand(expr_or_eqn.lhs), expand(expr_or_eqn.rhs))

    else:
        return expr_or_eqn.new(sympy.expand(expr_or_eqn.val))


SubstitutionMap = Dict[AbstractPhysicalQuantity, Q[AbstractPhysicalQuantity]]


@overload
def subs(
    expr_or_eqn: GPhysicalQuantity, substitutions: SubstitutionMap
) -> GPhysicalQuantity:
    ...


@overload
def subs(expr_or_eqn: Equation, substitutions: SubstitutionMap) -> Equation:
    ...


def subs(
    expr_or_eqn: Union[GPhysicalQuantity, Equation],
    substitutions: SubstitutionMap,
) -> Union[GPhysicalQuantity, Equation]:
    if isinstance(expr_or_eqn, Equation):
        return Equation(
            subs(expr_or_eqn.lhs, substitutions),
            subs(expr_or_eqn.rhs, substitutions),
        )

    else:
        sympy_subsmap = {}

        for from_, to in substitutions.items():
            if not isinstance(to, AbstractPhysicalQuantity):
                to = from_.__class__(from_.units, to)

            sympy_subsmap[from_.val] = to.in_units(from_).val

        return expr_or_eqn.__class__(
            expr_or_eqn.units, expr_or_eqn.val.subs(sympy_subsmap)
        )
