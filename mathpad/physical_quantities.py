import sympy.physics.units.definitions as u
import sympy.physics.units.definitions.dimension_definitions as d

from mathpad.physical_quantity import AbstractPhysicalQuantity, Dimensionless

# TODO: rearrange in alphabetical order


class Length(AbstractPhysicalQuantity):
    dimension = d.length


class Time(AbstractPhysicalQuantity):
    dimension = d.time


class Impedance(AbstractPhysicalQuantity):
    dimension = d.impedance


class Resistivity(AbstractPhysicalQuantity):
    dimension = d.impedance * d.length


class Inductance(AbstractPhysicalQuantity):
    dimension = d.inductance


class Capacitance(AbstractPhysicalQuantity):
    dimension = d.capacitance


class Mass(AbstractPhysicalQuantity):
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


class Frequency(AbstractPhysicalQuantity):
    dimension = d.frequency


class Current(AbstractPhysicalQuantity):
    dimension = d.current


class Action(AbstractPhysicalQuantity):
    dimension = d.action


class AmountOfSubstance(AbstractPhysicalQuantity):
    dimension = d.amount_of_substance


class Radioactivity(AbstractPhysicalQuantity):
    # same SI unit as frequency but is (should be?) treated differently
    dimension = 1 / d.time


class Charge(AbstractPhysicalQuantity):
    dimension = d.charge


class Dioptre(AbstractPhysicalQuantity):
    # technicaly "Optical/Refractive Power" but this is more obvious
    dimension = 1 / d.length


class Lumosity(AbstractPhysicalQuantity):
    dimension = d.luminous_intensity


class GravityConstant(AbstractPhysicalQuantity):
    # useful to name this as a type; but is only ever a constant (defined in constants.py)
    dimension = d.length ** 3 / (d.mass * d.time ** 2)


class Gray(AbstractPhysicalQuantity):
    # technicaly measurement of "Absorbed Dose" but this is more obvious
    dimension = d.energy / d.mass


class Energy(AbstractPhysicalQuantity):
    dimension = d.energy


class Temperature(AbstractPhysicalQuantity):
    dimension = d.temperature


class Force(AbstractPhysicalQuantity):
    dimension = d.force


class Pressure(AbstractPhysicalQuantity):
    dimension = d.pressure


class MolarGasConstant(AbstractPhysicalQuantity):
    # useful to name this as a specific dimension; but is only ever a constant (defined in constants.py)
    dimension = d.energy / (d.amount_of_substance * d.temperature)


class Conductance(AbstractPhysicalQuantity):
    dimension = d.conductance


class MagneticDensity(AbstractPhysicalQuantity):
    dimension = d.magnetic_density


class MagneticFlux(AbstractPhysicalQuantity):
    dimension = d.magnetic_flux


class Voltage(AbstractPhysicalQuantity):
    dimension = d.voltage


class Power(AbstractPhysicalQuantity):
    dimension = d.power


class Acceleration(AbstractPhysicalQuantity):
    dimension = d.acceleration


class Information(AbstractPhysicalQuantity):
    dimension = d.information


class Velocity(AbstractPhysicalQuantity):
    dimension = d.velocity


class LuminousIntensity(AbstractPhysicalQuantity):
    dimension = d.luminous_intensity


class Area(AbstractPhysicalQuantity):
    dimension = d.length ** 2


class Volume(AbstractPhysicalQuantity):
    dimension = d.length ** 3


class Permittivity(AbstractPhysicalQuantity):
    dimension = d.capacitance / d.length


class Katal(AbstractPhysicalQuantity):
    # Otherwise 'catalytic activity'
    dimension = d.amount_of_substance / d.time


class Illuminance(AbstractPhysicalQuantity):
    dimension = d.luminous_intensity / d.length ** 2


class Density(AbstractPhysicalQuantity):
    dimension = d.mass / d.length ** 3


class EnergyDensity(AbstractPhysicalQuantity):
    dimension = d.energy / d.length ** 3


class PlanckIntensity(AbstractPhysicalQuantity):
    # TODO; can/should we merge this with LuminousIntensity?
    dimension = d.mass / d.time ** 3


class Momentum(AbstractPhysicalQuantity):
    dimension = d.mass * d.velocity
