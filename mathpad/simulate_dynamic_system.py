from typing import Collection, Set, List, Optional, Tuple

import sympy
from sympy.core.function import Function, AppliedUndef
from sympy import Derivative
import plotly.graph_objects as go
from sympy.utilities.lambdify import lambdify
from scipy.integrate import RK45
from IPython.display import display

from mathpad.physical_quantity import AbstractPhysicalQuantity
from mathpad.equation import Equation
from mathpad.algebra import subs, SubstitutionMap, simplify
from mathpad._quality_of_life import t


def simulate_dynamic_system(
    dynamics_equations: Collection[Equation],
    *,
    x_f: float,
    initial_conditions: SubstitutionMap,
    record: List[AbstractPhysicalQuantity],
    max_step: Optional[float],
    substitute: SubstitutionMap = {},
    x_axis: AbstractPhysicalQuantity = t,
    display_equations: bool = True,
    display_plots: bool = True,
    all_solutions: bool = True,
    interactive_plots: bool = True,
) -> List[List[Tuple[float, List[float]]]]:
    "simulates a differential system specified by dynamics_equations from initial conditions at x_axis=0 (typically t=0) to x_final"

    # TODO: support integrals
    if max_step is None:
        max_step = float("inf")

    # pre-substitute and simplify the input equations before further processing
    problem_eqns = [simplify(subs(eqn, substitute)) for eqn in dynamics_equations]

    # collect derivatives and any unspecified unkowns
    derivatives: Set[Tuple[Function, float]] = set()

    for eqn in problem_eqns:
        sympy_eqn = eqn.as_sympy_eq()
        # TODO: properly check x_axis for derivative collection (usually t)
        derivatives.update(
            {
                (d.args[0], d.args[1][1] if isinstance(d.args[1], sympy.Tuple) else 1)
                for d in sympy_eqn.atoms(Derivative)
            }
        )
        derivatives.update(
            {(f, 0) for f in sympy_eqn.atoms(Function) if isinstance(f, AppliedUndef)}
        )

    highest_derivatives = {}
    lowest_derivatives = {}
    for f, lvl in derivatives:

        if f in highest_derivatives:
            if highest_derivatives[f] < lvl:
                highest_derivatives[f] = lvl
        else:
            highest_derivatives[f] = lvl

        if f in lowest_derivatives:
            if lowest_derivatives[f] > lvl:
                lowest_derivatives[f] = lvl
        else:
            lowest_derivatives[f] = lvl

    solve_for_highest_derivatives = [
        fn if lvl == 0 else sympy.diff(fn, (x_axis.val, lvl))
        for fn, lvl in highest_derivatives.items()
    ]

    solve_for_recorded_data = [pqty.val for pqty in record]

    solve_for = solve_for_highest_derivatives + solve_for_recorded_data

    if display_equations:
        print("Solving Equations:")
        for eqn in problem_eqns:
            display(eqn)

    solutions = sympy.solve(
        [eqn.as_sympy_eq() for eqn in problem_eqns],
        solve_for_highest_derivatives,
        dict=True,
    )

    assert any(solutions), "sympy solving failed!"

    all_data = []

    for solution_idx, solution in enumerate(solutions):

        # in dict mode, if a solution is equal to the query the solution is not included in the dict
        # we need it down the line, so re-insert it here:
        for val in solve_for:
            if val not in solution:
                solution[val] = val

        # convert it to a vector for lambdify below
        solution_vec = [solution[val] for val in solve_for]

        unknowns = set()
        for val in solution.values():
            unknowns.update(val.free_symbols)

        # since we're simulating along the x_axis, it doesn't count as an unknown here
        unknowns.remove(x_axis.val)

        assert not any(
            unknowns
        ), f"Cannot simulate ODE in the prescence of unknowns: {unknowns}. Please include them in substitutions"

        inputs = []
        not_lowest_derivative_list = []

        for fn, lowest_lvl in lowest_derivatives.items():
            highest_lvl = highest_derivatives[fn]
            not_lowest_derivative_list.append(False)
            not_lowest_derivative_list.extend([True] * (highest_lvl - lowest_lvl - 1))
            inputs.extend(
                [
                    fn if lvl == 0 else sympy.diff(fn, (x_axis.val, lvl))
                    for lvl in range(lowest_lvl, highest_lvl)
                ]
            )

        lambdified = lambdify([x_axis.val, inputs], solution_vec)

        data = []

        n_unique_derivatives = len(solve_for_highest_derivatives)

        def step(x, state):
            output = lambdified(x, state)
            highest_derivatives = output[:n_unique_derivatives]
            data.append((x, output[n_unique_derivatives:]))

            res = [
                s
                for s, not_lowest_derivative in zip(state, not_lowest_derivative_list)
                if not_lowest_derivative
            ] + highest_derivatives
            return res

        # normalize and check initial conditions
        y0 = []
        for sym in inputs:
            sym_hash = hash(sym)
            # find the original pqty
            # this is backwards, and this whole function could probably use a refactor
            for pqty in initial_conditions.keys():
                if hash(pqty) == sym_hash:
                    break
            else:
                assert False

            replacement = initial_conditions[pqty]
            if isinstance(replacement, AbstractPhysicalQuantity):
                val = float(replacement.in_units(pqty).val)
            else:
                val = replacement

            y0.append(val)

        integrator = RK45(step, t0=0, y0=y0, t_bound=x_f, max_step=max_step)

        while integrator.status == "running":
            msg = integrator.step()

            if integrator.status == "failed":
                print(f"integration completed with failed status: {msg}")
                break

        if display_plots:
            go.Figure(
                [
                    go.Scatter(
                        x=[t for t, _ in data],
                        y=[frame[idx] for _, frame in data],
                        name=str(sym),
                    )
                    for idx, sym in enumerate(record)
                ],
                layout=dict(title=f"Solution #{solution_idx + 1}"),
            ).show(None if interactive_plots else "svg")

        all_data.extend(data)

        if not all_solutions:
            break

    return all_data
