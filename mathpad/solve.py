from typing import Collection, Dict, Set, Tuple, Union, overload
from ansitable import ANSITable
import sympy

from mathpad.physical_quantity import AbstractPhysicalQuantity, GPhysicalQuantity
from mathpad.equation import Equation


class Solution:
    def __init__(
        self, result_dict: Dict[AbstractPhysicalQuantity, AbstractPhysicalQuantity]
    ):
        self.result_dict = result_dict

    def __getitem__(self, k: GPhysicalQuantity) -> GPhysicalQuantity:
        result = self.result_dict[k]
        assert result.units == k.units
        return result

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
        table = ANSITable(
            "  unknown  ", "  solutions  ", border="thick", bordercolor="green"
        )
        for k, v in self.result_dict.items():
            table.row(k, v)
        table.print()


@overload
def solve(
    equations: Equation, solve_for: AbstractPhysicalQuantity, in_place: bool = False
) -> Solution:
    ...


@overload
def solve(
    equations: Collection[Equation],
    solve_for: Collection[AbstractPhysicalQuantity],
    in_place: bool = False,
) -> Solution:
    ...


def solve(
    equations: Union[Equation, Collection[Equation]],
    solve_for: Union[AbstractPhysicalQuantity, Collection[AbstractPhysicalQuantity]],
    in_place: bool = False,
    # domain: Literal["complex", "real", "integers", "naturals", "naturals0"] = "real",
) -> Solution:
    # normalize inputs
    if isinstance(solve_for, AbstractPhysicalQuantity):
        solve_for = (solve_for,)
    if isinstance(equations, Equation):
        equations = (equations,)

    assert len(equations) >= len(
        solve_for
    ), "Systems with less equations than unknowns are typically unsolveable"

    ukwn_syms = [ukwn.val for ukwn in solve_for]
    val_eqns = [eqn.as_sympy_eq() for eqn in equations]
    # units_eqns = [eqn.as_units_eq_without_unknowns(unknowns) for eqn in equations]

    # TODO: allow arbitrary expressions to be used here and substitute symbols for the user
    for sym in ukwn_syms:
        assert isinstance(sym, sympy.Expr)

    # treat integrals and derivatives like

    # TODO: add more domains. Are there more?
    # domain_set = {
    #     "real": S.Reals,
    #     "complex": S.Complexes,
    #     "integers": S.Integers,
    #     "naturals": S.Naturals0,
    #     "naturals0": S.Naturals0,
    # }

    results: Dict[sympy.Expr, sympy.Expr] = sympy.solve(val_eqns, ukwn_syms)  # type: ignore

    if not any(results):
        raise Exception("Solving failed!")

    solution = Solution(
        {unkwn: unkwn.__class__(unkwn.units, results[unkwn.val]) for unkwn in solve_for}
    )  # type: ignore

    if in_place:
        for unknown, result in solution.result_dict.items():
            unknown.val = result.val

    return solution