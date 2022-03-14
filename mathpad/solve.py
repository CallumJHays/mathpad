from typing import Collection, Dict, List, Tuple, Union, overload
from ansitable import ANSITable
import sympy

from mathpad.val import Val, GenericVal
from mathpad.equation import Equation


class Solution:
    def __init__(self, result_dict: Dict[Val, Val]):
        self.result_dict = result_dict

    def __getitem__(self, k: GenericVal) -> GenericVal:
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

    def tabulate(self):
        table = ANSITable(
            "  unknown  ", "  solutions  ", border="thick", bordercolor="green"
        )
        for k, v in self.result_dict.items():
            table.row(k, v)
        table.print()

    def ipython_display(self):
        from IPython.display import display
        for ukwn, result in self.result_dict.items():
            display(ukwn == result)


@overload
def solve(equations: Equation, solve_for: Val, quiet: bool = False) -> Union[Solution, List[Solution]]:
    ...


@overload
def solve(
    equations: Collection[Equation],
    solve_for: Collection[Val],
    quiet: bool = False
) -> Union[Solution, List[Solution]]:
    ...


def solve(
    equations: Union[Equation, Collection[Equation]],
    solve_for: Union[Val, Collection[Val]],
    quiet: bool = False
    # domain: Literal["complex", "real", "integers", "naturals", "naturals0"] = "real",
) -> Union[Solution, List[Solution]]:
    # normalize inputs
    if isinstance(solve_for, Val):
        solve_for = (solve_for,)
    if isinstance(equations, Equation):
        equations = (equations,)

    # assert len(equations) >= len(
    #     solve_for
    # ), "Systems with less equations than unknowns are typically unsolveable"

    ukwn_syms = [ukwn.val for ukwn in solve_for]
    val_eqns = [eqn.as_sympy_eq() for eqn in equations]
    # units_eqns = [eqn.as_units_eq_without_unknowns(unknowns) for eqn in equations]

    if not quiet:
        from IPython.display import display
        print(f"Solving {len(val_eqns)} equations:")
        for eqn in equations:
            display(eqn)

        print("For values:")
        display(solve_for)

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

    results = sympy.solve(val_eqns, ukwn_syms)  # type: ignore

    if not any(results):
        raise Exception("Solving failed!")

    if isinstance(results, dict):
        results: Dict[sympy.Expr, sympy.Expr]
        sln = Solution(
            {unkwn: unkwn.__class__(
                unkwn.units, results[unkwn.val]) for unkwn in solve_for}
        )
        if not quiet:
            print("Found solution!")
            sln.ipython_display()
        return sln

    elif isinstance(results, list):
        results: List[Tuple[sympy.Expr, ...]]
        slns = [Solution(
            {var: var.__class__(var.units, val)
             for var, val in zip(solve_for, result)}
        ) for result in results]
        if not quiet:
            if len(slns) == 1:
                print("Found Solution!")
            else:
                print(f"Found {len(slns)} solutions. Solution #1 is:")

            slns[0].ipython_display()
        return slns[0] if len(slns) == 1 else slns

    else:
        print("[mathpad] WARNING: sympy solve resulted in unexpected datatype. Returning it directly...")
        return results
