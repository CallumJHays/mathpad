from typing import Type, cast
from mathpad import *
        

@mathpad_constructor
def kinetic_energy(*, m: X[Mass], v: X[Velocity]) -> Energy:
    """
    Calculate the kinetic energy of a particle.

    Args:
        m: Mass of the particle
        v: Velocity of the particle
    
    Returns:
        Kinetic energy of the particle in joules

    Example:
        >>> kinetic_energy(m=1 * kg, v=2 * m/s)
        2 joules
        >>> kinetic_energy(m="m" * kg, v="v" * m/s)
        0.5*mv**2 joules

    """
    return (m * v ** 2 / 2).in_units(joules)  # type: ignore


@mathpad_constructor
def elastic_energy(*, k: X[Elasticity], dx: X[Length]) -> Energy:
    return k * dx ** 2 / 2  # type: ignore


@mathpad_constructor
def gravitational_energy(*, m: X[Mass], h: X[Length], g: X[Acceleration]) -> Energy:
    return m * g * h  # type: ignore


@mathpad_constructor
def euler_lagrange(
    *,
    KE: X[Energy],
    PE: X[Energy],
    NCF: X[Force],
    var: Val,
) -> Equation:
    """
    Euler-Lagrange equation for a system of particles.

    Arguments:
        sum_KE: sum of kinetic energies of particles
        sum_PE: sum of potential energies of particles
        sum_NCF: sum of net contact forces on particles
        var: variable you are interested in finding the dynamics for
    
    """
    L = KE - PE
    return diff(diff(L, wrt=diff(var)), wrt=t) - diff(L, wrt=var) == NCF # type: ignore


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
