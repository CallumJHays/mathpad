from typing import Collection, Dict, List, Union, overload

import sympy
from sympy.solvers.solveset import linsolve

from mathpad.physical_quantity import (
    AbstractPhysicalQuantity,
    GPhysicalQuantity,
    PhysicalQuantity,
)
from mathpad.equation import Equation


class Solution:
    def __init__(
        self, result_dict: Dict[AbstractPhysicalQuantity, AbstractPhysicalQuantity]
    ):
        self.result_dict = result_dict

    def __getitem__(self, k: GPhysicalQuantity) -> GPhysicalQuantity:
        return k.__class__(k.units, self.result_dict[k])

    def __repr__(self):
        return self._repr("", " ")

    def _repr(self, newline: str, indent: str):
        # TODO: print latex
        return (
            f"Solution({newline}{indent}"
            + f",{newline}{indent}".join(
                f"{key.val} = {val}" for key, val in self.result_dict.items()
            )
            + f"{newline}{' ' if not newline else ''})"
        )

    def print(self):
        print(self._repr("\n", "    "))


@overload
def solve(
    unknowns: AbstractPhysicalQuantity, equations: Equation, in_place: bool = False
) -> Solution:
    ...


@overload
def solve(
    unknowns: Collection[AbstractPhysicalQuantity],
    equations: Collection[Equation],
    in_place: bool = False,
) -> Solution:
    ...


def solve(
    unknowns: Union[AbstractPhysicalQuantity, Collection[AbstractPhysicalQuantity]],
    equations: Union[Equation, Collection[Equation]],
    in_place: bool = False
    # domain: sympy.Set = sympy.Complexes
) -> Solution:
    # normalize inputs
    if isinstance(unknowns, AbstractPhysicalQuantity):
        unknowns = (unknowns,)
    if isinstance(equations, Equation):
        equations = (equations,)

    # TODO: allow more equations than unknowns, somehow. Have to play around with linsolve
    assert len(equations) == len(unknowns)

    ukwn_syms = [ukwn.val for ukwn in unknowns]
    val_eqns = [eqn.as_sympy_eq() for eqn in equations]
    # units_eqns = [eqn.as_units_eq_without_unknowns(unknowns) for eqn in equations]

    # TODO: allow arbitrary expressions to be used here and substitute symbols for the user
    for sym in ukwn_syms:
        assert isinstance(sym, sympy.Symbol)

    results: List[sympy.Symbol] = linsolve(val_eqns, ukwn_syms)
    # result_units = linsolve()
    # results_typed = []

    if not any(results):
        raise Exception("Solving failed!")

    solution = Solution(
        {
            expr: expr.__class__(expr.units, result[0] if len(result) == 1 else result)
            for expr, result in zip(unknowns, zip(*results))
        }
    )  # type: ignore

    if in_place:
        for unknown, result in solution.result_dict.items():
            unknown.val = result.val

    return solution