from typing import Collection, Dict, List, Union, overload, Any

import sympy
from sympy.solvers.solveset import linsolve, nonlinsolve
from sympy.core.relational import Equality

from mathpad.physical_quantity import Equation, GPhysicalQuantity, PhysicalQuantity


class SolveResult(Dict[PhysicalQuantity, PhysicalQuantity]):
    def __init__(self, result_dict: Dict[PhysicalQuantity, PhysicalQuantity]):
        self.result_dict = result_dict

    def __getitem__(self, k: GPhysicalQuantity) -> GPhysicalQuantity:
        return k.__class__(
            k.units,
            self.result_dict[k],  # type: ignore
            k.dimension
        )

    def __repr__(self):
        # TODO: print latex
        return "SolveResult(\n    " + ",\n    ".join(
            f"{key.val} = {val} {key.units}" for key, val in self.result_dict.items()
        ) + "\n)"


@overload
def solve(unknowns: PhysicalQuantity, equations: Equation,
          in_place: bool = False) -> SolveResult: ...


@overload
def solve(
    unknowns: Collection[PhysicalQuantity],
    equations: Collection[Equation],
    in_place: bool = False
) -> SolveResult: ...


def solve(
    unknowns: Union[PhysicalQuantity, Collection[PhysicalQuantity]],
    equations: Union[Equation, Collection[Equation]],
    in_place: bool = False
    # domain: sympy.Set = sympy.Complexes
) -> SolveResult:
    # normalize inputs
    if isinstance(unknowns, PhysicalQuantity):
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

    result_vals: List[sympy.Symbol] = linsolve(val_eqns, ukwn_syms)
    # result_units = linsolve()
    results_typed = []

    if not any(results):
        raise Exception("Solving failed!")

    return SolveResult({
        expr: result[0] if len(result) == 1 else result
        for expr, result in zip(unknowns, zip(*results))
    })  # type: ignore
