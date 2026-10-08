from typing import Literal
from math import pi
from langchain_core.tools import tool


@tool
def heat_transfer(
    operation: Literal[
        "conduction",
        "convection",
        "radiation",
        "heat_rate",
    ],
    thermal_conductivity: float | None = None,
    area: float | None = None,
    temperature_difference: float | None = None,
    thickness: float | None = None,
    convection_coefficient: float | None = None,
    surface_temperature: float | None = None,
    fluid_temperature: float | None = None,
    emissivity: float | None = None,
    surface_temperature_radiation: float | None = None,
    surroundings_temperature: float | None = None,
    heat_rate_value: float | None = None,
) -> float:
    """
    Calculate heat transfer by conduction, convection, and radiation.

    ---------------------------------------------------------
    1. CONDUCTION
    ---------------------------------------------------------

    Fourier's law for one-dimensional steady conduction
    through a flat wall:

        Q_dot = k * A * ΔT / L

    where:

        Q_dot = heat-transfer rate [W]
        k     = thermal conductivity [W/(m*K)]
        A     = area [m^2]
        ΔT    = temperature difference [K]
        L     = wall thickness [m]

    ---------------------------------------------------------
    2. CONVECTION
    ---------------------------------------------------------

    Newton's law of cooling:

        Q_dot = h * A * (Ts - Tinf)

    where:

        h    = convection coefficient [W/(m^2*K)]
        A    = surface area [m^2]
        Ts   = surface temperature [K or °C]
        Tinf = fluid/bulk temperature [K or °C]

    ---------------------------------------------------------
    3. RADIATION
    ---------------------------------------------------------

    Stefan-Boltzmann equation:

        Q_dot = ε * σ * A * (Ts^4 - Tsur^4)

    where:

        ε    = surface emissivity
        σ    = Stefan-Boltzmann constant
             = 5.670374419e-8 W/(m^2*K^4)
        A    = radiating area [m^2]
        Ts   = surface absolute temperature [K]
        Tsur = surroundings absolute temperature [K]

    Radiation temperatures MUST be in Kelvin.

    ---------------------------------------------------------
    4. HEAT RATE
    ---------------------------------------------------------

    If heat_rate_value is supplied, the tool returns it.

    Otherwise, heat_rate calculates the heat-transfer rate
    using the available heat-transfer information.

    Supported modes:

        conduction
        convection
        radiation

    ---------------------------------------------------------
    SIGN CONVENTION
    ---------------------------------------------------------

    Positive heat rate:
        heat flows from the hotter region toward the colder
        region.

    Negative heat rate:
        the supplied temperature ordering causes heat flow in
        the opposite direction.

    Units:

        heat rate -> W
        area -> m^2
        thickness -> m
        temperature difference -> K
        conductivity -> W/(m*K)
        convection coefficient -> W/(m^2*K)
        emissivity -> dimensionless
    """

    # Stefan-Boltzmann constant
    SIGMA = 5.670374419e-8

    # ---------------------------------------------------------
    # CONDUCTION
    # ---------------------------------------------------------

    if operation == "conduction":

        if thermal_conductivity is None:
            raise ValueError(
                "thermal_conductivity is required "
                "for conduction."
            )

        if area is None:
            raise ValueError(
                "area is required for conduction."
            )

        if temperature_difference is None:
            raise ValueError(
                "temperature_difference is required "
                "for conduction."
            )

        if thickness is None:
            raise ValueError(
                "thickness is required for conduction."
            )

        if thermal_conductivity <= 0:
            raise ValueError(
                "thermal_conductivity must be greater than zero."
            )

        if area <= 0:
            raise ValueError(
                "area must be greater than zero."
            )

        if thickness <= 0:
            raise ValueError(
                "thickness must be greater than zero."
            )

        # Fourier's law:
        #
        # Q_dot = k*A*ΔT/L

        return (
            thermal_conductivity
            * area
            * temperature_difference
            / thickness
        )

    # ---------------------------------------------------------
    # CONVECTION
    # ---------------------------------------------------------

    elif operation == "convection":

        if convection_coefficient is None:
            raise ValueError(
                "convection_coefficient is required "
                "for convection."
            )

        if area is None:
            raise ValueError(
                "area is required for convection."
            )

        if surface_temperature is None:
            raise ValueError(
                "surface_temperature is required "
                "for convection."
            )

        if fluid_temperature is None:
            raise ValueError(
                "fluid_temperature is required "
                "for convection."
            )

        if convection_coefficient < 0:
            raise ValueError(
                "convection_coefficient cannot be negative."
            )

        if area <= 0:
            raise ValueError(
                "area must be greater than zero."
            )

        # Newton's law:
        #
        # Q_dot = h*A*(Ts - Tinf)

        return (
            convection_coefficient
            * area
            * (
                surface_temperature
                - fluid_temperature
            )
        )

    # ---------------------------------------------------------
    # RADIATION
    # ---------------------------------------------------------

    elif operation == "radiation":

        if emissivity is None:
            raise ValueError(
                "emissivity is required for radiation."
            )

        if area is None:
            raise ValueError(
                "area is required for radiation."
            )

        if surface_temperature_radiation is None:
            raise ValueError(
                "surface_temperature_radiation is required "
                "for radiation."
            )

        if surroundings_temperature is None:
            raise ValueError(
                "surroundings_temperature is required "
                "for radiation."
            )

        if not 0 <= emissivity <= 1:
            raise ValueError(
                "emissivity must be between 0 and 1."
            )

        if area <= 0:
            raise ValueError(
                "area must be greater than zero."
            )

        if surface_temperature_radiation <= 0:
            raise ValueError(
                "surface_temperature_radiation must be "
                "greater than zero Kelvin."
            )

        if surroundings_temperature <= 0:
            raise ValueError(
                "surroundings_temperature must be "
                "greater than zero Kelvin."
            )

        # Stefan-Boltzmann:
        #
        # Q_dot = εσA(Ts^4 - Tsur^4)

        return (
            emissivity
            * SIGMA
            * area
            * (
                surface_temperature_radiation**4
                - surroundings_temperature**4
            )
        )

    # ---------------------------------------------------------
    # HEAT RATE
    # ---------------------------------------------------------

    elif operation == "heat_rate":

        if heat_rate_value is not None:

            return heat_rate_value

        raise ValueError(
            "heat_rate requires heat_rate_value. "
            "Alternatively use conduction, convection, "
            "or radiation to calculate the heat rate."
        )

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )