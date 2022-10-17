import sympy.physics.units.definitions as u
import sympy.physics.units.definitions.dimension_definitions as d

from mathpad.val import Unit, Dimensionless

# TODO: rearrange in alphabetical order

__all__ = [
    "Dimensionless",
    "Length",
    "Time",
    "AngularMomentum",
    "AngularVelocity",
    "MomentOfInertia",
    "Impedance",
    "Resistivity",
    "Inductance",
    "Capacitance",
    "Mass",
    "Angle",
    "AngularMil",
    "SteRadian",
    "Frequency",
    "Current",
    "Action",
    "AmountOfSubstance",
    "Radioactivity",
    "Charge",
    "Dioptre",
    "Lumosity",
    "GravityConstant",
    "Gray",
    "Energy",
    "Temperature",
    "Force",
    "Elasticity",
    "Pressure",
    "MolarGasConstant",
    "Conductance",
    "MagneticDensity",
    "MagneticFlux",
    "Voltage",
    "Power",
    "Acceleration",
    "Information",
    "Velocity",
    "LuminousIntensity",
    "Area",
    "Volume",
    "Permittivity",
    "Katal",
    "Illuminance",
    "Density",
    "EnergyDensity",
    "PlanckIntensity",
    "Momentum"
]


class Length(Unit):
    dimension = d.length
    base_units = u.meter


class Time(Unit):
    dimension = d.time
    base_units = u.second


class AngularMomentum(Unit):
    dimension = d.mass * d.velocity * d.angle
    base_units = u.kg * u.meter * u.second


class AngularVelocity(Unit):
    dimension = d.angle / d.time
    base_units = u.radian / u.second


class MomentOfInertia(Unit):
    dimension = d.mass / d.length ** 2
    base_units = u.kg / u.meter ** 2


class Impedance(Unit):
    dimension = d.impedance
    base_units = u.ohm


class Resistivity(Unit):
    dimension = d.impedance * d.length
    base_units = u.ohm * u.meter


class Inductance(Unit):
    dimension = d.inductance
    base_units = u.henry


class Capacitance(Unit):
    dimension = d.capacitance
    base_units = u.farad


class Mass(Unit):
    dimension = d.mass
    base_units = u.kg


# todo: figure out how to merge all Angle classes into one


class Angle(Dimensionless):
    # TODO: get deg, angular_mil and (maybe) steradian to use angle
    dimension = d.angle
    base_units = u.radian


class AngularMil(Angle):
    # has its own dimension for some reason
    dimension = u.angular_mil.dimension # type: ignore
    base_units = u.angular_mil


class SteRadian(Angle):
    # this one's interesting because it's something like m**2 / m**2
    # subclass 'angle' but use its special dimension
    # TODO: review if this is gonna cause issues
    dimension = u.steradian.dimension # type: ignore
    base_units = u.steradian


class Frequency(Unit):
    # TODO: does this make sense as a dimension?
    dimension = d.frequency
    base_units = u.hertz


class Current(Unit):
    dimension = d.current
    base_units = u.ampere


class Action(Unit):
    dimension = d.action
    base_units = u.joule * u.second


class AmountOfSubstance(Unit):
    # TODO: difference between this and Mass?
    dimension = d.amount_of_substance
    base_units = u.mole


class Radioactivity(Unit):
    # same SI unit as frequency but is (should be?) treated differently
    dimension = 1 / d.time
    base_units = u.becquerel


class Charge(Unit):
    dimension = d.charge
    base_units = u.coulomb


class Dioptre(Unit):
    # technicaly "Optical/Refractive Power" but this is more obvious
    dimension = 1 / d.length
    base_units = u.dioptre


class Lumosity(Unit):
    dimension = d.luminous_intensity
    base_units = u.candela * u.steradian


class GravityConstant(Unit):
    dimension = d.length ** 3 / (d.mass * d.time ** 2)
    base_units = u.gravitational_constant


class Gray(Unit):
    # technicaly measurement of "Absorbed Dose" but this is more obvious
    dimension = d.energy / d.mass
    base_units = u.gray


class Energy(Unit):
    dimension = d.energy
    base_units = u.joule


class Temperature(Unit):
    dimension = d.temperature
    base_units = u.kelvin


class Force(Unit):
    dimension = d.force
    base_units = u.newton


class Elasticity(Unit):
    dimension = d.force / d.length
    base_units = u.pascal


class Pressure(Unit):
    dimension = d.pressure
    base_units = u.pascal


class MolarGasConstant(Unit):
    # Is only ever used to define a constant (in constants.py)
    dimension = d.energy / (d.amount_of_substance * d.temperature)
    base_units = u.molar_gas_constant


class Conductance(Unit):
    dimension = d.conductance
    base_units = u.siemens


class MagneticDensity(Unit):
    dimension = d.magnetic_density
    base_units = u.tesla


class MagneticFlux(Unit):
    dimension = d.magnetic_flux
    base_units = u.weber


class Voltage(Unit):
    dimension = d.voltage
    base_units = u.volt


class Power(Unit):
    dimension = d.power
    base_units = u.watt


class Acceleration(Unit):
    dimension = d.acceleration
    base_units = u.meter / u.second ** 2


class Information(Unit):
    dimension = d.information
    base_units = u.bit


class Velocity(Unit):
    dimension = d.velocity
    base_units = u.meter / u.second


class LuminousIntensity(Unit):
    dimension = d.luminous_intensity
    base_units = u.candela


class Area(Unit):
    dimension = d.length ** 2
    base_units = u.meter ** 2


class Volume(Unit):
    dimension = d.length ** 3
    base_units = u.meter ** 3


class Permittivity(Unit):
    dimension = d.capacitance / d.length
    base_units = u.farad / u.meter


class Katal(Unit):
    "Also known as 'catalytic activity'"
    dimension = d.amount_of_substance / d.time
    base_units = u.katal


class Illuminance(Unit):
    dimension = d.luminous_intensity / d.length ** 2
    base_units = u.lux


class Density(Unit):
    dimension = d.mass / d.length ** 3
    base_units = u.kg / u.meter ** 3


class EnergyDensity(Unit):
    dimension = d.energy / d.length ** 3
    base_units = u.joule / u.meter ** 3


class PlanckIntensity(Unit):
    dimension = d.mass / d.time ** 3
    base_units = u.joule / u.second ** 3


class Momentum(Unit):
    dimension = d.mass * d.velocity
    base_units = u.kg * u.meter / u.second
