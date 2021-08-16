import sympy.physics.units.definitions as u
import sympy.physics.units.definitions.dimension_definitions as d

from .physical_quantity import PhysicalQuantity

# TODO: rearrange in alphabetical order


class Length(PhysicalQuantity):
    dimension = d.length


class Time(PhysicalQuantity):
    dimension = d.time


class Impedance(PhysicalQuantity):
    dimension = d.impedance


class Resistivity(PhysicalQuantity):
    dimension = d.impedance * d.length


class Inductance(PhysicalQuantity):
    dimension = d.inductance


class Capacitance(PhysicalQuantity):
    dimension = d.capacitance


class Mass(PhysicalQuantity):
    dimension = d.mass

# todo: figure out how to merge all Angle classes into one


class Angle(PhysicalQuantity):
    # TODO: get deg, angular_mil and (maybe) steradian to use angle
    dimension = d.angle


class AngleDeg(Angle):
    # because deg.dimension != angle
    dimension = d.Dimension(1)  # type: ignore


class AngleAngularMil(Angle):
    "Not the same as milli-radians"
    # because deg.dimension != angle
    dimension = u.angular_mil.dimension


class SteRadian(PhysicalQuantity):
    # this one's interesting because it's something like m**2 / m**2
    # TODO: should this be an Angle?
    dimension = u.steradian.dimension


class Frequency(PhysicalQuantity):
    dimension = d.frequency


class Current(PhysicalQuantity):
    dimension = d.current


class Action(PhysicalQuantity):
    dimension = d.action


class AmountOfSubstance(PhysicalQuantity):
    dimension = d.amount_of_substance


class Radioactivity(PhysicalQuantity):
    # same SI unit as frequency but is (should be?) treated differently
    dimension = 1 / d.time


class Charge(PhysicalQuantity):
    dimension = d.charge


class Dioptre(PhysicalQuantity):
    # technicaly "Optical/Refractive Power" but this is more obvious
    dimension = 1 / d.length


class Lumosity(PhysicalQuantity):
    dimension = d.luminous_intensity


class GravityConstant(PhysicalQuantity):
    # useful to name this as a type; but is only ever a constant (defined in constants.py)
    dimension = d.length**3 / (d.mass * d.time**2)


class Gray(PhysicalQuantity):
    # technicaly measurement of "Absorbed Dose" but this is more obvious
    dimension = d.energy / d.mass


class Energy(PhysicalQuantity):
    dimension = d.energy


class Temperature(PhysicalQuantity):
    dimension = d.temperature


class Force(PhysicalQuantity):
    dimension = d.force


class Pressure(PhysicalQuantity):
    dimension = d.pressure


class MolarGasConstant(PhysicalQuantity):
    # useful to name this as a specific dimension; but is only ever a constant (defined in constants.py)
    dimension = d.energy / (d.amount_of_substance * d.temperature)


class Conductance(PhysicalQuantity):
    dimension = d.conductance


class MagneticDensity(PhysicalQuantity):
    dimension = d.magnetic_density


class MagneticFlux(PhysicalQuantity):
    dimension = d.magnetic_flux


class Voltage(PhysicalQuantity):
    dimension = d.voltage


class Power(PhysicalQuantity):
    dimension = d.power


class Acceleration(PhysicalQuantity):
    dimension = d.acceleration


class AngularMil(PhysicalQuantity):
    dimension = d.angle


class Information(PhysicalQuantity):
    dimension = d.information


class Velocity(PhysicalQuantity):
    dimension = d.velocity


class LuminousIntensity(PhysicalQuantity):
    dimension = d.luminous_intensity


class Area(PhysicalQuantity):
    dimension = d.length ** 2


class Volume(PhysicalQuantity):
    dimension = d.length ** 3


class Permittivity(PhysicalQuantity):
    dimension = d.capacitance / d.length


class Katal(PhysicalQuantity):
    # Otherwise 'catalytic activity'
    dimension = d.amount_of_substance / d.time


class Illuminance(PhysicalQuantity):
    dimension = d.luminous_intensity / d.length**2


class Density(PhysicalQuantity):
    dimension = d.mass / d.length**3


class EnergyDensity(PhysicalQuantity):
    dimension = d.energy / d.length**3


class PlanckIntensity(PhysicalQuantity):
    # TODO; can/should we merge this with LuminousIntensity?
    dimension = d.mass / d.time**3


class Momentum(PhysicalQuantity):
    dimension = d.mass * d.velocity
