from typing import TYPE_CHECKING, Collection, Dict, List, Union, overload
import sympy

from mathpad.core.val import Val, ValT
from mathpad.core.equation import Equation
if TYPE_CHECKING:
    from mathpad.core.vector import Vector, VecT


class Solution:
    def __init__(self, result_dict: Dict[Union[Val, 'Vector'], Union[Val, 'Vector']]):
        self.result_dict = result_dict

    @overload
    def __getitem__(self, key: ValT) -> ValT:
        ...
    
    @overload
    def __getitem__(self, key: 'VecT') -> 'VecT':
        ...

    
    def __getitem__(self, k: Union[ValT, 'VecT']) -> Union[ValT, 'VecT']: # type: ignore
        from mathpad.core import Vector
        result = self.result_dict[k]
        if isinstance(result, Val):
            assert result.units == k.units
        elif isinstance(result, Vector):
            assert result.frame.space == k.frame.space # type: ignore
        return result # type: ignore

    def __repr__(self):
        return self._repr("", " ")

    def _repr(self, newline: str, indent: str):
        # TODO: print latex
        return (
            f"Solution({newline}{indent}"
            + f",{newline}{indent}".join(
                f"{key.expr} = {val}" for key, val in self.result_dict.items()
            )
            + f"{newline}{' ' if not newline else ''})"
        )
    
    def items(self):
        return self.result_dict.items()

def solve(
    equations: Collection[Equation],
    solve_for: Collection[Union[Val, 'Vector']]
    # domain: Literal["complex", "real", "integers", "naturals", "naturals0"] = "real",
) -> List[Solution]:
    from mathpad.core import Vector
    
    solve_for_vectors_split: List[Val] = []
    for x in solve_for:
        if isinstance(x, Vector):
            solve_for_vectors_split += list(x)
        else:
            solve_for_vectors_split.append(x)

    assert len(equations) >= len(
        solve_for
    ), "Systems with less equations than unknowns are typically unsolvable"

    ukwn_syms = [ukwn.expr for ukwn in solve_for_vectors_split]
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

    results: List[Dict[sympy.Expr, sympy.Expr]] = \
        sympy.solve(val_eqns, ukwn_syms, dict=True)  # type: ignore

    if not any(results):
        raise Exception("Solving failed!")
    
    solutions = []
    for result in results:
        
        val_result = {
            unkwn: unkwn.__class__(unkwn.units, result[unkwn.expr])
            for unkwn in solve_for_vectors_split
        }

        slnmap = {}
        for x in solve_for:
            if isinstance(x, Vector):
                # reassemble vector from components
                slnmap[x] = Vector(x.space, [val_result[unkwn] for unkwn in x])
            else:
                slnmap[x] = val_result[x]

        solution = Solution(slnmap)
        solutions.append(solution)

    return solutions
