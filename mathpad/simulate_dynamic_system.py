from typing import Collection, Set, List, Optional, Tuple
from itertools import zip_longest

import sympy
import numpy as np
from sympy.core.function import Function, AppliedUndef
from sympy import Derivative
import plotly.graph_objects as go
from sympy.utilities.lambdify import lambdify
from scipy.integrate import RK45
from IPython.display import display
import plotly.io as pio

from mathpad.val import Val
from mathpad.equation import Equation
from mathpad.algebra import subs, SubstitutionMap, simplify
from mathpad._quality_of_life import t
from tqdm.notebook import tqdm


def simulate_dynamic_system(
    dynamics_equations: Collection[Equation],
    *,
    x_f: float,
    initial_conditions: SubstitutionMap,
    record: List[Val],
    max_step: Optional[float],
    substitute: SubstitutionMap = {},
    x_axis: Val = t,
    all_solutions: bool = False,
    # output display options
    verbose: bool = True,
    display_plots: bool = True,
    display_progress_bar: bool = True,
    display_explanation: bool = False,
    # plot formatting (display_plots=True)
    plot_static: bool = False,
    plot_static_figsize: Tuple[int, int] = (960, 400),
    plot_title: str = "Solution #{solutionNo}",
) -> List[List[Tuple[float, List[float]]]]:
    "simulates a differential system specified by dynamics_equations from initial conditions at x_axis=0 (typically t=0) to x_final"

    verbose = verbose or display_explanation

    if plot_static_figsize and not plot_static:
        print(
            "Warning: plot_static_figsize was set but plot_static was not enabled. Enabling for you automatically. Set plot_static=True to "
        )

    # make static renderings a certain size, the default one is too square for my liking
    svg_renderer = pio.renderers["svg"]
    width, height = plot_static_figsize
    svg_renderer.width = width
    svg_renderer.height = height

    # TODO: support plotting on separate axes, and subplots
    # TODO: ensure we aren't subbing out something that is required for a 'record' output

    # TODO: support integrals
    if max_step is None:
        max_step = float("inf")

    if display_explanation:
        print("Using Input Equations:")
        for eqn in dynamics_equations:
            display(eqn)

        print("Subbing in Values:")
        for replace, _with in substitute.items():
            display(replace == _with)

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

    solve_for_recorded_data = [val.val for val in record]

    solve_for = solve_for_highest_derivatives + solve_for_recorded_data

    _print_if(verbose, f"Solving subbed Equations{':' if display_explanation else ''}")

    if display_explanation:
        for eqn in problem_eqns:
            display(eqn)

        print("For values:")
        display(solve_for)

    solutions = sympy.solve(
        [eqn.as_sympy_eq() for eqn in problem_eqns],
        solve_for_highest_derivatives,
        dict=True,
    )

    assert any(solutions), "sympy solving failed!"
    _print_if(verbose, "Solving finished.")

    all_data = []

    for solution_idx, solution in enumerate(solutions):

        # in dict mode, if a solution is equal to the query the solution is not included in the dict
        # we need it down the line, so re-insert it here:
        for val in solve_for:
            if val not in solution:
                solution[val] = val

        # convert it to a vector for lambdify below
        solution_vec = [solution[val] for val in solve_for]

        if display_explanation:
            print(
                "Found Solution" + (f"#{solution_idx + 1}:" if all_solutions else ":")
            )
            for solve_val, result in zip(solve_for, solution_vec):
                eqn = sympy.Eq(solve_val, result)
                if eqn != True:  # this happens with passthrough variables
                    display(eqn)

        unknowns = set()
        for val in solution.values():
            unknowns.update(val.free_symbols)

        # since we're simulating along the x_axis, it doesn't count as an unknown here
        unknowns.remove(x_axis.val)

        assert not any(
            unknowns
        ), f"Cannot simulate ODE in the prescence of unknowns: {unknowns}. Please include them in substitutions"

        input_unzipped = []

        for fn, lowest_lvl in lowest_derivatives.items():
            highest_lvl = highest_derivatives[fn]
            input_unzipped.append(
                [
                    fn if lvl == 0 else sympy.diff(fn, (x_axis.val, lvl))
                    for lvl in range(lowest_lvl, highest_lvl)
                ]
            )

        # inputs are lowest to highest derivatives excluding the highest, ie [x, y, dx, dy]
        inputs = [
            deriv
            for derivatives in zip_longest(*input_unzipped)
            for deriv in derivatives
            if deriv is not None
        ]

        # outputs are highest of input derviatives plus recorded data
        # ie [dddx, record[0], record[1]]
        lambdified = lambdify([x_axis.val, inputs], solution_vec)

        data = []

        n_unique_derivatives = len(highest_derivatives)

        # define this integration function to record data and let outputs = diff(inputs)
        def step(x: float, state: np.ndarray):

            output = lambdified(x, state)

            highest_derivatives, recorded_data = (
                output[:n_unique_derivatives],
                output[n_unique_derivatives:],
            )

            data.append((x, recorded_data))

            dstate = np.append(state[n_unique_derivatives:], highest_derivatives)
            return dstate

        # normalize and check initial conditions
        y0 = []
        for sym in inputs:
            sym_hash = hash(sym)
            # find the original val
            # this is backwards, and this whole function could probably use a refactor
            for val in initial_conditions.keys():
                if hash(val) == sym_hash:  # because (hash(val) == hash(val.val))
                    break
            else:
                assert (
                    sym in initial_conditions
                ), f"Required initial condition missing: {sym}"

            replacement = initial_conditions[val]
            if isinstance(replacement, Val):
                val = float(replacement.in_units(val).val)
            else:
                val = replacement

            y0.append(val)

        integrator = RK45(step, t0=0, y0=y0, t_bound=x_f, max_step=max_step)

        _print_if(
            verbose,
            f"Simulating from t=0 to t={x_f} with a max_step of {max_step}"
            + (" with initial conditions:" if display_explanation else "."),
        )

        if display_explanation:
            for replace, _with in initial_conditions.items():
                display(replace == _with)

        t_prev = 0

        with tqdm(total=x_f, leave=False) if display_progress_bar else None as pbar:
            while integrator.status == "running":
                msg = integrator.step()

                if integrator.status == "failed":
                    print(f"integration completed with failed status: {msg}")
                    break

                if pbar:
                    dt = integrator.t - t_prev
                    pbar.update(dt)
                    t_prev = integrator.t

        _print_if(verbose, "Simulation finished. Plotting...")

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
                layout={
                    "xaxis": {"title": str(x_axis)},
                    "title": {
                        "text": plot_title.format(solutionNo=solution_idx + 1),
                        "y": 0.9,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                    },
                },
            ).show("svg" if plot_static else None)

        all_data.extend(data)

        if not all_solutions:
            break

    return all_data


def _print_if(condition: bool, msg: str):
    if condition:
        print(msg)