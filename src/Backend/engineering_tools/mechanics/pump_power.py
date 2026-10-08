from typing import Literal
from langchain_core.tools import tool


@tool
def pump_power(
    operation: Literal[
        "hydraulic_power",
        "shaft_power",
        "pump_head",
    ],
    flow_rate: float,
    pressure_difference: float | None = None,
    head: float | None = None,
    density: float = 1000.0,
    efficiency: float = 1.0,
    gravity: float = 9.81,
) -> float:
    """
    Calculate pump hydraulic power, shaft power, and pump head.

    ---------------------------------------------------------
    1. HYDRAULIC POWER
    ---------------------------------------------------------

    Hydraulic power:

        P_h = Q * DeltaP

    where:

        P_h = hydraulic power [W]
        Q   = volumetric flow rate [m^3/s]
        DeltaP = pressure increase [Pa]

    Hydraulic power can also be calculated from head:

        P_h = rho * g * Q * H

    where:

        rho = fluid density [kg/m^3]
        g   = gravitational acceleration [m/s^2]
        H   = pump head [m]

    ---------------------------------------------------------
    2. SHAFT POWER
    ---------------------------------------------------------

    Shaft power is the hydraulic power divided by pump efficiency:

        P_shaft = P_h / eta

    Therefore:

        P_shaft = Q * DeltaP / eta

    or:

        P_shaft = rho * g * Q * H / eta

    where:

        eta = pump efficiency

    Efficiency must be between 0 and 1.

    ---------------------------------------------------------
    3. PUMP HEAD
    ---------------------------------------------------------

    Pump head from pressure difference:

        H = DeltaP / (rho * g)

    where:

        H = pump head [m]
        DeltaP = pressure difference [Pa]
        rho = fluid density [kg/m^3]
        g = gravitational acceleration [m/s^2]

    Units:

        flow_rate        -> m^3/s
        pressure_difference -> Pa
        density          -> kg/m^3
        head             -> m
        efficiency       -> 0 to 1
        hydraulic power  -> W
        shaft power      -> W

    Assumptions:

        - Steady-state operation
        - Constant fluid density
        - Pump efficiency is known
        - Pressure_difference represents the pressure
          increase produced by the pump
    """

    # ---------------------------------------------------------
    # COMMON VALIDATION
    # ---------------------------------------------------------

    if flow_rate <= 0:
        raise ValueError(
            "flow_rate must be greater than zero."
        )

    if density <= 0:
        raise ValueError(
            "density must be greater than zero."
        )

    if gravity <= 0:
        raise ValueError(
            "gravity must be greater than zero."
        )

    if efficiency <= 0 or efficiency > 1:
        raise ValueError(
            "efficiency must be greater than 0 "
            "and less than or equal to 1."
        )

    # ---------------------------------------------------------
    # HYDRAULIC POWER
    # ---------------------------------------------------------

    if operation == "hydraulic_power":

        # Option 1:
        # P_h = Q * DeltaP

        if pressure_difference is not None:

            if pressure_difference <= 0:
                raise ValueError(
                    "pressure_difference must be greater than zero."
                )

            hydraulic_power = (
                flow_rate * pressure_difference
            )

            return hydraulic_power

        # Option 2:
        # P_h = rho*g*Q*H

        if head is not None:

            if head <= 0:
                raise ValueError(
                    "head must be greater than zero."
                )

            hydraulic_power = (
                density
                * gravity
                * flow_rate
                * head
            )

            return hydraulic_power

        raise ValueError(
            "hydraulic_power requires either "
            "pressure_difference or head."
        )

    # ---------------------------------------------------------
    # SHAFT POWER
    # ---------------------------------------------------------

    elif operation == "shaft_power":

        if pressure_difference is not None:

            if pressure_difference <= 0:
                raise ValueError(
                    "pressure_difference must be greater than zero."
                )

            hydraulic_power = (
                flow_rate * pressure_difference
            )

        elif head is not None:

            if head <= 0:
                raise ValueError(
                    "head must be greater than zero."
                )

            hydraulic_power = (
                density
                * gravity
                * flow_rate
                * head
            )

        else:

            raise ValueError(
                "shaft_power requires either "
                "pressure_difference or head."
            )

        # P_shaft = P_h / eta

        shaft_power = (
            hydraulic_power / efficiency
        )

        return shaft_power

    # ---------------------------------------------------------
    # PUMP HEAD
    # ---------------------------------------------------------

    elif operation == "pump_head":

        if pressure_difference is None:
            raise ValueError(
                "pressure_difference is required "
                "for pump_head."
            )

        if pressure_difference <= 0:
            raise ValueError(
                "pressure_difference must be greater than zero."
            )

        # H = DeltaP / (rho*g)

        pump_head_value = (
            pressure_difference
            / (density * gravity)
        )

        return pump_head_value

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )