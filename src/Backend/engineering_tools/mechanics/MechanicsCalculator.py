from langchain_core.tools import tool
from src.Exceptions import MechMind
from src.Logger import logging
import math
import numpy

from langchain_core.tools import tool


@tool
def calculate_force(mass: float, acceleration: float) -> float:
    """
    Calculate force using Newton's second law.

    Formula:
        F = m * a

    Args:
        mass: Mass in kilograms (kg).
        acceleration: Acceleration in meters per second squared (m/s²).

    Returns:
        Force in Newtons (N).
    """
    return mass * acceleration


@tool
def calculate_mass(force: float, acceleration: float) -> float:
    """
    Calculate mass from force and acceleration.

    Formula:
        m = F / a

    Args:
        force: Force in Newtons (N).
        acceleration: Acceleration in meters per second squared (m/s²).

    Returns:
        Mass in kilograms (kg).
    """
    if acceleration == 0:
        raise ValueError("Acceleration cannot be zero.")

    return force / acceleration


@tool
def calculate_acceleration(force: float, mass: float) -> float:
    """
    Calculate acceleration from force and mass.

    Formula:
        a = F / m

    Args:
        force: Force in Newtons (N).
        mass: Mass in kilograms (kg).

    Returns:
        Acceleration in meters per second squared (m/s²).
    """
    if mass == 0:
        raise ValueError("Mass cannot be zero.")

    return force / mass


@tool
def calculate_torque(
    force: float,
    lever_arm: float,
    angle: float = 90.0,
) -> float:
    """
    Calculate torque.

    Formula:
        τ = r * F * sin(θ)

    Args:
        force: Force in Newtons (N).
        lever_arm: Distance from pivot in meters (m).
        angle: Angle between force and lever arm in degrees.

    Returns:
        Torque in Newton-meters (N·m).
    """
    import math

    return lever_arm * force * math.sin(math.radians(angle))


@tool
def calculate_work(
    force: float,
    displacement: float,
    angle: float = 0.0,
) -> float:
    """
    Calculate mechanical work.

    Formula:
        W = F * d * cos(θ)

    Args:
        force: Force in Newtons (N).
        displacement: Displacement in meters (m).
        angle: Angle between force and displacement in degrees.

    Returns:
        Work in Joules (J).
    """
    import math

    return force * displacement * math.cos(math.radians(angle))


@tool
def calculate_energy(
    mass: float,
    velocity: float,
) -> float:
    """
    Calculate kinetic energy.

    Formula:
        KE = 1/2 * m * v²

    Args:
        mass: Mass in kilograms (kg).
        velocity: Velocity in meters per second (m/s).

    Returns:
        Kinetic energy in Joules (J).
    """

    return 0.5 * mass * velocity ** 2


@tool
def calculate_power(
    work: float,
    time: float,
) -> float:
    """
    Calculate mechanical power.

    Formula:
        P = W / t

    Args:
        work: Work in Joules (J).
        time: Time in seconds (s).

    Returns:
        Power in Watts (W).
    """
    if time == 0:
        raise ValueError("Time cannot be zero.")

    return work / time


@tool
def calculate_stress(
    force: float,
    area: float,
) -> float:
    """
    Calculate normal stress.

    Formula:
        σ = F / A

    Args:
        force: Force in Newtons (N).
        area: Cross-sectional area in square meters (m²).

    Returns:
        Stress in Pascals (Pa).
    """
    if area == 0:
        raise ValueError("Area cannot be zero.")

    return force / area


@tool
def calculate_strain(
    change_in_length: float,
    original_length: float,
) -> float:
    """
    Calculate normal strain.

    Formula:
        ε = ΔL / L₀

    Args:
        change_in_length: Change in length in meters (m).
        original_length: Original length in meters (m).

    Returns:
        Strain (dimensionless).
    """
    if original_length == 0:
        raise ValueError("Original length cannot be zero.")

    return change_in_length / original_length