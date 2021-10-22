import sympy.physics.units.definitions as u
import sympy.physics.units.definitions.dimension_definitions as d

from mathpad.physical_quantity import Unit, Dimensionless

# TODO: rearrange in alphabetical order


class Length(Unit):
    dimension = d.length


class Time(Unit):
    dimension = d.time


class AngularMomentum(Unit):
    dimension = d.mass * d.velocity * d.angle


class Impedance(Unit):
    dimension = d.impedance


class Resistivity(Unit):
    dimension = d.impedance * d.length


class Inductance(Unit):
    dimension = d.inductance


class Capacitance(Unit):
    dimension = d.capacitance


class Mass(Unit):
    dimension = d.mass


# todo: figure out how to merge all Angle classes into one


class Angle(Dimensionless):
    # TODO: get deg, angular_mil and (maybe) steradian to use angle
    dimension = d.angle


class AngularMil(Angle):
    # has its own dimension for some reason
    dimension = u.angular_mil.dimension


class SteRadian(Angle):
    # this one's interesting because it's something like m**2 / m**2
    # subclass 'angle' but use its special dimension
    # TODO: review if this is gonna cause issues
    dimension = u.steradian.dimension


class Frequency(Unit):
    dimension = d.frequency


class Current(Unit):
    dimension = d.current


class Action(Unit):
    dimension = d.action


class AmountOfSubstance(Unit):
    dimension = d.amount_of_substance


class Radioactivity(Unit):
    # same SI unit as frequency but is (should be?) treated differently
    dimension = 1 / d.time


class Charge(Unit):
    dimension = d.charge


class Dioptre(Unit):
    # technicaly "Optical/Refractive Power" but this is more obvious
    dimension = 1 / d.length


class Lumosity(Unit):
    dimension = d.luminous_intensity


class GravityConstant(Unit):
    # useful to name this as a type; but is only ever a constant (defined in constants.py)
    dimension = d.length ** 3 / (d.mass * d.time ** 2)


class Gray(Unit):
    # technicaly measurement of "Absorbed Dose" but this is more obvious
    dimension = d.energy / d.mass


class Energy(Unit):
    dimension = d.energy


class Temperature(Unit):
    dimension = d.temperature


class Force(Unit):
    dimension = d.force


class Elasticity(Unit):
    dimension = d.force / d.length


class Pressure(Unit):
    dimension = d.pressure


class MolarGasConstant(Unit):
    # useful to name this as a specific dimension; but is only ever a constant (defined in constants.py)
    dimension = d.energy / (d.amount_of_substance * d.temperature)


class Conductance(Unit):
    dimension = d.conductance


class MagneticDensity(Unit):
    dimension = d.magnetic_density


class MagneticFlux(Unit):
    dimension = d.magnetic_flux


class Voltage(Unit):
    dimension = d.voltage


class Power(Unit):
    dimension = d.power


class Acceleration(Unit):
    dimension = d.acceleration


class Information(Unit):
    dimension = d.information


class Velocity(Unit):
    dimension = d.velocity


class LuminousIntensity(Unit):
    dimension = d.luminous_intensity


class Area(Unit):
    dimension = d.length ** 2


class Volume(Unit):
    dimension = d.length ** 3


class Permittivity(Unit):
    dimension = d.capacitance / d.length


class Katal(Unit):
    # Otherwise 'catalytic activity'
    dimension = d.amount_of_substance / d.time


class Illuminance(Unit):
    dimension = d.luminous_intensity / d.length ** 2


class Density(Unit):
    dimension = d.mass / d.length ** 3


class EnergyDensity(Unit):
    dimension = d.energy / d.length ** 3


class PlanckIntensity(Unit):
    # TODO; can/should we merge this with LuminousIntensity?
    dimension = d.mass / d.time ** 3


class Momentum(Unit):
    dimension = d.mass * d.velocity
