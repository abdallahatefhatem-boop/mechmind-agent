from typing import Literal
from langchain_core.tools import tool


@tool
def pressure_vessel(
    operation: Literal[
        "hoop_stress",
        "longitudinal_stress",
        "wall_thickness",
    ],
    pressure: float,
    radius: float | None = None,
    diameter: float | None = None,
    wall_thickness_value: float | None = None,
    allowable_stress: float | None = None,
    weld_efficiency: float = 1.0,
) -> float:
    """
    Calculate stresses and required wall thickness for a
    thin-walled cylindrical pressure vessel.

    ---------------------------------------------------------
    1. HOOP STRESS
    ---------------------------------------------------------

    Circumferential/hoop stress:

        sigma_h = P*r/t

    or:

        sigma_h = P*D/(2*t)

    where:

        P = internal pressure
        r = vessel internal radius
        D = vessel internal diameter
        t = wall thickness

    Hoop stress is the stress around the circumference of
    the vessel.

    ---------------------------------------------------------
    2. LONGITUDINAL STRESS
    ---------------------------------------------------------

    Longitudinal stress:

        sigma_L = P*r/(2*t)

    or:

        sigma_L = P*D/(4*t)

    For a closed-end thin-walled cylindrical vessel:

        sigma_h = 2 * sigma_L

    ---------------------------------------------------------
    3. WALL THICKNESS
    ---------------------------------------------------------

    Required wall thickness based on hoop stress:

        t = P*r / (S*E)

    or:

        t = P*D / (2*S*E)

    where:

        S = allowable material stress
        E = weld/joint efficiency

    Units:
        pressure       -> Pa
        radius/diameter -> m
        thickness      -> m
        stress         -> Pa

    Example:
        pressure = 1 MPa
        diameter = 1 m
        allowable_stress = 100 MPa
        weld_efficiency = 1.0

    Important:
        This is a thin-wall analytical calculator.
        Real pressure-vessel design should follow the applicable
        code/standard such as ASME Section VIII and consider
        corrosion allowance, openings, nozzles, temperature,
        external pressure, weld details, fatigue, and safety
        factors.

        For wall_thickness, the hoop-stress criterion is used
        because hoop stress is the larger principal stress.
    """

    # ---------------------------------------------------------
    # COMMON VALIDATION
    # ---------------------------------------------------------

    if pressure <= 0:
        raise ValueError(
            "pressure must be greater than zero."
        )

    if weld_efficiency <= 0 or weld_efficiency > 1:
        raise ValueError(
            "weld_efficiency must be greater than 0 "
            "and less than or equal to 1."
        )

    # ---------------------------------------------------------
    # GET RADIUS
    # ---------------------------------------------------------

    if radius is not None:

        if radius <= 0:
            raise ValueError(
                "radius must be greater than zero."
            )

        vessel_radius = radius

    elif diameter is not None:

        if diameter <= 0:
            raise ValueError(
                "diameter must be greater than zero."
            )

        vessel_radius = diameter / 2.0

    else:

        raise ValueError(
            "Either radius or diameter is required."
        )

    # ---------------------------------------------------------
    # HOOP STRESS
    # ---------------------------------------------------------

    if operation == "hoop_stress":

        if wall_thickness_value is None:
            raise ValueError(
                "wall_thickness_value is required "
                "for hoop_stress."
            )

        if wall_thickness_value <= 0:
            raise ValueError(
                "wall_thickness_value must be greater than zero."
            )

        # Thin-wall equation:
        #
        # sigma_h = P*r/t

        hoop_stress = (
            pressure * vessel_radius
        ) / wall_thickness_value

        return hoop_stress

    # ---------------------------------------------------------
    # LONGITUDINAL STRESS
    # ---------------------------------------------------------

    elif operation == "longitudinal_stress":

        if wall_thickness_value is None:
            raise ValueError(
                "wall_thickness_value is required "
                "for longitudinal_stress."
            )

        if wall_thickness_value <= 0:
            raise ValueError(
                "wall_thickness_value must be greater than zero."
            )

        # Thin-wall equation:
        #
        # sigma_L = P*r/(2*t)

        longitudinal_stress = (
            pressure * vessel_radius
        ) / (
            2 * wall_thickness_value
        )

        return longitudinal_stress

    # ---------------------------------------------------------
    # WALL THICKNESS
    # ---------------------------------------------------------

    elif operation == "wall_thickness":

        if allowable_stress is None:
            raise ValueError(
                "allowable_stress is required "
                "for wall_thickness."
            )

        if allowable_stress <= 0:
            raise ValueError(
                "allowable_stress must be greater than zero."
            )

        # Required thickness based on hoop stress:
        #
        # P*r/t <= S*E
        #
        # Therefore:
        #
        # t >= P*r/(S*E)

        required_thickness = (
            pressure * vessel_radius
        ) / (
            allowable_stress * weld_efficiency
        )

        return required_thickness

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )