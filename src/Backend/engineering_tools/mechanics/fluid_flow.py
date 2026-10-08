from typing import Literal
from math import pi, log10
from langchain_core.tools import tool


@tool
def fluid_flow(
    operation: Literal[
        "reynolds_number",
        "pressure_loss",
        "flow_rate",
        "velocity",
    ],
    density: float,
    viscosity: float,
    pipe_diameter: float | None = None,
    pipe_length: float | None = None,
    velocity_value: float | None = None,
    flow_rate_value: float | None = None,
    pressure_loss_value: float | None = None,
    roughness: float = 0.0,
) -> float:
    """
    Calculate basic fluid-flow parameters for flow through a circular pipe.

    ---------------------------------------------------------
    REYNOLDS NUMBER
    ---------------------------------------------------------

        Re = rho * V * D / mu

    where:
        rho = fluid density [kg/m^3]
        V   = average fluid velocity [m/s]
        D   = pipe diameter [m]
        mu  = dynamic viscosity [Pa.s]

    Flow regime:
        Re < 2300       -> approximately laminar
        2300-4000       -> transitional
        Re > 4000       -> turbulent

    ---------------------------------------------------------
    FLOW RATE
    ---------------------------------------------------------

        Q = V * A

    For a circular pipe:

        A = pi * D^2 / 4

    Therefore:

        Q = V * pi * D^2 / 4

    ---------------------------------------------------------
    VELOCITY
    ---------------------------------------------------------

        V = Q / A

    Therefore:

        V = 4Q / (pi * D^2)

    ---------------------------------------------------------
    PRESSURE LOSS
    ---------------------------------------------------------

    Darcy-Weisbach equation:

        Delta_P = f * (L/D) * (rho*V^2/2)

    where:
        f = Darcy friction factor
        L = pipe length [m]
        D = pipe diameter [m]

    Friction factor:

    Laminar:
        f = 64/Re

    Turbulent:
        Swamee-Jain approximation:

        f = 0.25 /
            [log10(e/(3.7D) + 5.74/Re^0.9)]^2

    where:
        e = absolute pipe roughness [m]

    The tool automatically determines the flow regime from Re.

    Units:
        density        -> kg/m^3
        viscosity      -> Pa.s
        diameter       -> m
        length         -> m
        velocity       -> m/s
        flow rate      -> m^3/s
        pressure loss  -> Pa
        roughness      -> m

    Assumptions:
        - Circular pipe
        - Steady flow
        - Newtonian fluid
        - Constant properties
        - Fully developed internal flow
        - Darcy-Weisbach pressure loss
        - Minor losses from valves/fittings are not included
    """

    # ---------------------------------------------------------
    # COMMON VALIDATION
    # ---------------------------------------------------------

    if density <= 0:
        raise ValueError(
            "density must be greater than zero."
        )

    if viscosity <= 0:
        raise ValueError(
            "viscosity must be greater than zero."
        )

    if roughness < 0:
        raise ValueError(
            "roughness cannot be negative."
        )

    # ---------------------------------------------------------
    # REYNOLDS NUMBER
    # ---------------------------------------------------------

    if operation == "reynolds_number":

        if pipe_diameter is None:
            raise ValueError(
                "pipe_diameter is required for reynolds_number."
            )

        if velocity_value is None:
            raise ValueError(
                "velocity_value is required for reynolds_number."
            )

        if pipe_diameter <= 0:
            raise ValueError(
                "pipe_diameter must be greater than zero."
            )

        if velocity_value < 0:
            raise ValueError(
                "velocity_value cannot be negative."
            )

        reynolds = (
            density
            * velocity_value
            * pipe_diameter
            / viscosity
        )

        return reynolds

    # ---------------------------------------------------------
    # FLOW RATE
    # ---------------------------------------------------------

    elif operation == "flow_rate":

        if pipe_diameter is None:
            raise ValueError(
                "pipe_diameter is required for flow_rate."
            )

        if velocity_value is None:
            raise ValueError(
                "velocity_value is required for flow_rate."
            )

        if pipe_diameter <= 0:
            raise ValueError(
                "pipe_diameter must be greater than zero."
            )

        if velocity_value < 0:
            raise ValueError(
                "velocity_value cannot be negative."
            )

        # Cross-sectional area
        area = pi * pipe_diameter**2 / 4

        # Q = V*A
        return velocity_value * area

    # ---------------------------------------------------------
    # VELOCITY
    # ---------------------------------------------------------

    elif operation == "velocity":

        if pipe_diameter is None:
            raise ValueError(
                "pipe_diameter is required for velocity."
            )

        if flow_rate_value is None:
            raise ValueError(
                "flow_rate_value is required for velocity."
            )

        if pipe_diameter <= 0:
            raise ValueError(
                "pipe_diameter must be greater than zero."
            )

        if flow_rate_value < 0:
            raise ValueError(
                "flow_rate_value cannot be negative."
            )

        # V = Q/A
        area = pi * pipe_diameter**2 / 4

        return flow_rate_value / area

    # ---------------------------------------------------------
    # PRESSURE LOSS
    # ---------------------------------------------------------

    elif operation == "pressure_loss":

        if pipe_diameter is None:
            raise ValueError(
                "pipe_diameter is required for pressure_loss."
            )

        if pipe_length is None:
            raise ValueError(
                "pipe_length is required for pressure_loss."
            )

        if velocity_value is None:
            raise ValueError(
                "velocity_value is required for pressure_loss."
            )

        if pipe_diameter <= 0:
            raise ValueError(
                "pipe_diameter must be greater than zero."
            )

        if pipe_length <= 0:
            raise ValueError(
                "pipe_length must be greater than zero."
            )

        if velocity_value < 0:
            raise ValueError(
                "velocity_value cannot be negative."
            )

        # -----------------------------------------------------
        # Reynolds number
        # -----------------------------------------------------

        reynolds = (
            density
            * velocity_value
            * pipe_diameter
            / viscosity
        )

        # No flow -> no friction pressure loss
        if reynolds == 0:
            return 0.0

        # -----------------------------------------------------
        # Darcy friction factor
        # -----------------------------------------------------

        if reynolds < 2300:

            # Laminar flow
            friction_factor = 64 / reynolds

        else:

            # Turbulent flow
            #
            # Swamee-Jain approximation
            #
            # f = 0.25 /
            #     [log10(e/(3.7D) + 5.74/Re^0.9)]^2

            relative_roughness = (
                roughness / pipe_diameter
            )

            friction_factor = (
                0.25
                / log10(
                    relative_roughness / 3.7
                    + 5.74 / reynolds**0.9
                )**2
            )

        # -----------------------------------------------------
        # Darcy-Weisbach equation
        # -----------------------------------------------------

        pressure_loss = (
            friction_factor
            * (pipe_length / pipe_diameter)
            * (density * velocity_value**2 / 2)
        )

        return pressure_loss

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )