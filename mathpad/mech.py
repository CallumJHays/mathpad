from typing import Type, cast
from mathpad import *
        

@mathpad_constructor
def kinetic_energy(*, m: X[Mass], v: X[Velocity]) -> Energy:
    "Energy of a moving object"
    return m * v ** 2 / 2  # type: ignore


@mathpad_constructor
def elastic_energy(*, k: X[Elasticity], dx: X[Length]) -> Energy:
    return k * dx ** 2 / 2  # type: ignore


@mathpad_constructor
def gravitational_energy(*, m: X[Mass], h: X[Length], g: X[Acceleration]) -> Energy:
    return m * g * h  # type: ignore


@mathpad_constructor
def euler_lagrange(
    *,
    sum_kinetic_energy: X[Energy],
    sum_potential_energy: X[Energy],
    sum_non_conservative_forces: X[Force],
    state: Val,
) -> Equation:
    """
    Euler-Lagrange equation for a system of particles.

    
    """
    L = sum_kinetic_energy - sum_potential_energy
    return diff(diff(L, wrt=diff(state)), wrt=t) - diff(L, wrt=state) == sum_non_conservative_forces # type: ignore


@mathpad_constructor
def impulse_momentum(
    *,
    m: X[Mass],  # mass
    v1: X[Velocity],  # initial velocity
    F: X[Force],  # impulse force required
    t: X[Time],  # impulse duration in seconds
    v2: X[Velocity],  # final velocity
) -> Equation:
    "The force required during an instant to change an object's velocity"
    return m * v1 + integral(F, wrt=t) == m * v2
