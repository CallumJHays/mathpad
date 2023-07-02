from mathpad import *
from .mathpad_constructor import mathpad_constructor
        

@mathpad_constructor
def kinetic_energy(*, m: Q[Mass], v: Q[Velocity]) -> Energy:
    """
    Calculate the kinetic energy of a particle.

    Args:
        m: Mass of the particle
        v: Velocity of the particle
    
    Returns:
        Kinetic energy of the particle in joules

    Example:
        >>> kinetic_energy(m="m" * kg, v="v" * m/s)
        0.5*mv**2 joules
        >>> kinetic_energy(m=1 * kg, v=2 * m/s)
        2 joules

    """
    return (m * v ** 2 / 2).in_units(joules)  # type: ignore


@mathpad_constructor
def elastic_energy(*, k: Q[Elasticity], dx: Q[Length]) -> Energy:
    return k * dx ** 2 / 2  # type: ignore


@mathpad_constructor
def gravitational_energy(*, m: Q[Mass], h: Q[Length], g: Q[Acceleration]) -> Energy:
    return m * g * h  # type: ignore


@mathpad_constructor
def euler_lagrange(
    *,
    KE: Q[Energy],
    PE: Q[Energy],
    NCF: Q[Force],
    var: Val,
) -> Equation[Force]:
    """
    Euler-Lagrange equation for a system of particles.

    Arguments:
        KE: sum of kinetic energies of particles
        PE: sum of potential energies of particles
        NCF: sum of net contact forces on particles
        var: variable you are interested in finding the dynamics for
    """
    L = KE - PE
    return diff(diff(L, wrt=diff(var)), wrt=t) - diff(L, wrt=var) == NCF # type: ignore


@mathpad_constructor
def impulse_momentum(
    *,
    m: Q[Mass],  # mass
    v1: Q[Velocity],  # initial velocity
    F: Q[Force],  # impulse force required
    t: Q[Time],  # impulse duration
    v2: Q[Velocity],  # final velocity
) -> Equation[Momentum]:
    "The force required during an instant to change an object's velocity"
    return m * v1 + integral(F, wrt=t) == m * v2
