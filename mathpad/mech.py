from mathpad import *


def kinetic_energy(m: Q[Mass], v: Q[Velocity]) -> Energy:
    "Energy of a moving object"
    return frac(1, 2) * m * v ** 2  # type: ignore


def elastic_energy(k: Q[Elasticity], dx: Q[Length]) -> Energy:
    return frac(1, 2) * k * dx ** 2  # type: ignore


def gravitational_energy(m: Q[Mass], h: Q[Length], g: Q[Acceleration] = g) -> Energy:
    return m * g * h  # type: ignore


def euler_lagrange(
    sum_kinetic_energy: Q[Energy],
    sum_potential_energy: Q[Energy],
    sum_non_conservative_forces: Q[Force],
    state: AbstractPhysicalQuantity,
) -> Equation:
    L = sum_kinetic_energy - sum_potential_energy
    ds = diff(state)
    return diff(diff(L, ds)) + diff(L, state) == sum_non_conservative_forces


def impulse_momentum(
    m: Q[Mass],  # mass
    v1: Q[Velocity],  # initial velocity
    F: Q[Force],  # impulse force required
    t: Q[Time],  # impulse duration in seconds
    v2: Q[Velocity],  # final velocity
) -> Equation:
    "The force required in an instant to change an object's velocity"
    return m * v1 + integral(F, t) == m * v2


def velocity_acceleration(
    v: Q[Velocity], t: Q[Time]  # symbol for time
) -> Acceleration:
    return a == integral(v, t)


def force_momentum(
    m: Q[Mass],  # mass of object
    v: Q[Velocity],
    t: Q[Time] = t,
) -> Force:
    return diff(m * v, t)


def angular_momentum(
    r_p_o: Q[Length],  # unit vector of rotation axis (anti-clockwise)
    m: Q[Mass],  # mass of point object
    v: Q[Velocity],  # velocity of point object
) -> AngularMomentum:
    return r_p_o.cross(m * v)