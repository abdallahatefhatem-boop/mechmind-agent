from typing import Literal
from langchain_core.tools import tool


@tool
def hvac_load(
    operation: Literal[
        "cooling_load",
        "heating_load",
        "sensible_heat",
        "latent_heat",
    ],
    # Common parameters
    area: float | None = None,
    temperature_difference: float | None = None,

    # Sensible heat
    mass_flow_rate: float | None = None,
    specific_heat: float = 1005.0,

    # Latent heat
    moisture_mass_flow_rate: float | None = None,
    latent_heat_vaporization: float = 2_500_000.0,

    # Building transmission
    thermal_transmittance: float | None = None,

    # Ventilation / infiltration
    air_flow_rate: float | None = None,
    air_density: float = 1.2,

    # Additional loads
    internal_sensible_load: float = 0.0,
    internal_latent_load: float = 0.0,
    solar_load: float = 0.0,

    # Heating-specific
    heating_efficiency: float = 1.0,
) -> float:
    """
    Estimate basic HVAC heating and cooling loads.

    ---------------------------------------------------------
    1. SENSIBLE HEAT
    ---------------------------------------------------------

        Q_sensible = m_dot * cp * ΔT

    where:

        m_dot = air mass flow rate [kg/s]
        cp    = specific heat [J/(kg*K)]
        ΔT    = temperature difference [K]

    ---------------------------------------------------------
    2. LATENT HEAT
    ---------------------------------------------------------

        Q_latent = m_dot_water * h_fg

    where:

        m_dot_water = moisture condensation/evaporation rate [kg/s]
        h_fg        = latent heat of vaporization [J/kg]

    ---------------------------------------------------------
    3. TRANSMISSION LOAD
    ---------------------------------------------------------

        Q_transmission = U * A * ΔT

    where:

        U  = overall heat-transfer coefficient [W/(m²*K)]
        A  = building area [m²]
        ΔT = indoor/outdoor temperature difference [K]

    ---------------------------------------------------------
    4. VENTILATION / INFILTRATION SENSIBLE LOAD
    ---------------------------------------------------------

        Q_ventilation = rho * V_dot * cp * ΔT

    where:

        rho   = air density [kg/m³]
        V_dot = volumetric airflow rate [m³/s]

    ---------------------------------------------------------
    5. COOLING LOAD
    ---------------------------------------------------------

        Q_cooling =
            transmission
            + ventilation
            + internal_sensible
            + solar
            + latent

    ---------------------------------------------------------
    6. HEATING LOAD
    ---------------------------------------------------------

        Q_heating =
            transmission
            + ventilation

        If heating_efficiency < 1:

            Required heater input =
                Q_heating / efficiency

    ---------------------------------------------------------
    Units
    ---------------------------------------------------------

        Heat/load       -> W
        Area            -> m²
        U-value         -> W/(m²*K)
        Temperature     -> K or °C difference
        Air flow        -> m³/s
        Mass flow       -> kg/s
        Specific heat   -> J/(kg*K)
        Latent heat     -> J/kg
    """

    # =========================================================
    # BASIC VALIDATION
    # =========================================================

    if specific_heat <= 0:
        raise ValueError(
            "specific_heat must be greater than zero."
        )

    if latent_heat_vaporization <= 0:
        raise ValueError(
            "latent_heat_vaporization must be greater than zero."
        )

    if air_density <= 0:
        raise ValueError(
            "air_density must be greater than zero."
        )

    if internal_sensible_load < 0:
        raise ValueError(
            "internal_sensible_load cannot be negative."
        )

    if internal_latent_load < 0:
        raise ValueError(
            "internal_latent_load cannot be negative."
        )

    if solar_load < 0:
        raise ValueError(
            "solar_load cannot be negative."
        )

    # =========================================================
    # SENSIBLE HEAT
    # =========================================================

    if operation == "sensible_heat":

        if mass_flow_rate is None:
            raise ValueError(
                "mass_flow_rate is required for sensible_heat."
            )

        if temperature_difference is None:
            raise ValueError(
                "temperature_difference is required "
                "for sensible_heat."
            )

        if mass_flow_rate < 0:
            raise ValueError(
                "mass_flow_rate cannot be negative."
            )

        return (
            mass_flow_rate
            * specific_heat
            * temperature_difference
        )

    # =========================================================
    # LATENT HEAT
    # =========================================================

    elif operation == "latent_heat":

        if moisture_mass_flow_rate is None:
            raise ValueError(
                "moisture_mass_flow_rate is required "
                "for latent_heat."
            )

        if moisture_mass_flow_rate < 0:
            raise ValueError(
                "moisture_mass_flow_rate cannot be negative."
            )

        return (
            moisture_mass_flow_rate
            * latent_heat_vaporization
        )

    # =========================================================
    # COOLING LOAD
    # =========================================================

    elif operation == "cooling_load":

        total_cooling_load = 0.0

        # ---------------------------------------------
        # 1. Building transmission
        # ---------------------------------------------

        if (
            area is not None
            and thermal_transmittance is not None
            and temperature_difference is not None
        ):

            if area <= 0:
                raise ValueError(
                    "area must be greater than zero."
                )

            if thermal_transmittance < 0:
                raise ValueError(
                    "thermal_transmittance cannot be negative."
                )

            transmission_load = (
                thermal_transmittance
                * area
                * abs(temperature_difference)
            )

            total_cooling_load += transmission_load

        # ---------------------------------------------
        # 2. Ventilation / infiltration
        # ---------------------------------------------

        if (
            air_flow_rate is not None
            and temperature_difference is not None
        ):

            if air_flow_rate < 0:
                raise ValueError(
                    "air_flow_rate cannot be negative."
                )

            ventilation_load = (
                air_density
                * air_flow_rate
                * specific_heat
                * abs(temperature_difference)
            )

            total_cooling_load += ventilation_load

        # ---------------------------------------------
        # 3. Internal sensible load
        # ---------------------------------------------

        total_cooling_load += internal_sensible_load

        # ---------------------------------------------
        # 4. Solar load
        # ---------------------------------------------

        total_cooling_load += solar_load

        # ---------------------------------------------
        # 5. Latent load
        # ---------------------------------------------

        if moisture_mass_flow_rate is not None:

            if moisture_mass_flow_rate < 0:
                raise ValueError(
                    "moisture_mass_flow_rate "
                    "cannot be negative."
                )

            latent_load = (
                moisture_mass_flow_rate
                * latent_heat_vaporization
            )

            total_cooling_load += latent_load

        total_cooling_load += internal_latent_load

        if total_cooling_load <= 0:
            raise ValueError(
                "Cooling load must be greater than zero. "
                "Provide at least one valid load component."
            )

        return total_cooling_load

    # =========================================================
    # HEATING LOAD
    # =========================================================

    elif operation == "heating_load":

        total_heating_load = 0.0

        # ---------------------------------------------
        # 1. Transmission heat loss
        # ---------------------------------------------

        if (
            area is not None
            and thermal_transmittance is not None
            and temperature_difference is not None
        ):

            if area <= 0:
                raise ValueError(
                    "area must be greater than zero."
                )

            if thermal_transmittance < 0:
                raise ValueError(
                    "thermal_transmittance "
                    "cannot be negative."
                )

            transmission_loss = (
                thermal_transmittance
                * area
                * abs(temperature_difference)
            )

            total_heating_load += transmission_loss

        # ---------------------------------------------
        # 2. Ventilation / infiltration heat loss
        # ---------------------------------------------

        if (
            air_flow_rate is not None
            and temperature_difference is not None
        ):

            if air_flow_rate < 0:
                raise ValueError(
                    "air_flow_rate cannot be negative."
                )

            ventilation_loss = (
                air_density
                * air_flow_rate
                * specific_heat
                * abs(temperature_difference)
            )

            total_heating_load += ventilation_loss

        if total_heating_load <= 0:
            raise ValueError(
                "Heating load must be greater than zero. "
                "Provide building transmission or "
                "ventilation parameters."
            )

        # Account for heater efficiency.
        if heating_efficiency <= 0 or heating_efficiency > 1:
            raise ValueError(
                "heating_efficiency must be > 0 and <= 1."
            )

        return total_heating_load / heating_efficiency

    # =========================================================
    # INVALID OPERATION
    # =========================================================

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )