from typing import Literal
from langchain_core.tools import tool


@tool
def beam_stress(
    operation: Literal[
        "bending_stress",
        "shear_stress",
        "bending_moment",
        "shear_force",
    ],
    force: float | None = None,
    distance: float | None = None,
    moment: float | None = None,
    c: float | None = None,
    inertia: float | None = None,
    area: float | None = None,
    first_moment_area: float | None = None,
    width: float | None = None,
) -> float:
    """
    Calculate beam stresses and internal forces.

    Supported operations:

    1. bending_stress
        Formula:
            sigma = M * c / I

        Required:
            moment
            c
            inertia

    2. shear_stress
        Formula:
            tau = V * Q / (I * b)

        Required:
            force
            first_moment_area
            inertia
            width

    3. bending_moment
        Formula:
            M = F * d

        Required:
            force
            distance

    4. shear_force
        Formula:
            V = F

        Required:
            force

    Parameters:
        force:
            Applied or internal force.

        distance:
            Perpendicular distance from force to the beam's
            reference point.

        moment:
            Bending moment.

        c:
            Distance from the neutral axis to the outermost
            fiber.

        inertia:
            Second moment of area (I).

        area:
            Cross-sectional area.

        first_moment_area:
            First moment of area (Q).

        width:
            Cross-sectional width at the location where
            shear stress is being calculated.

    Returns:
        Calculated engineering quantity as a float.
    """

    # =====================================================
    # BENDING STRESS
    # =====================================================

    if operation == "bending_stress":

        if moment is None:
            raise ValueError(
                "moment is required for bending_stress."
            )

        if c is None:
            raise ValueError(
                "c is required for bending_stress."
            )

        if inertia is None:
            raise ValueError(
                "inertia is required for bending_stress."
            )

        if inertia <= 0:
            raise ValueError(
                "Moment of inertia must be greater than zero."
            )

        result = (moment * c) / inertia

        return result

    # =====================================================
    # SHEAR STRESS
    # =====================================================

    elif operation == "shear_stress":

        if force is None:
            raise ValueError(
                "force is required for shear_stress."
            )

        if first_moment_area is None:
            raise ValueError(
                "first_moment_area (Q) is required "
                "for shear_stress."
            )

        if inertia is None:
            raise ValueError(
                "inertia (I) is required for shear_stress."
            )

        if width is None:
            raise ValueError(
                "width (b) is required for shear_stress."
            )

        if inertia <= 0:
            raise ValueError(
                "Moment of inertia must be greater than zero."
            )

        if width <= 0:
            raise ValueError(
                "Width must be greater than zero."
            )

        result = (
            force * first_moment_area
        ) / (
            inertia * width
        )

        return result

    # =====================================================
    # BENDING MOMENT
    # =====================================================

    elif operation == "bending_moment":

        if force is None:
            raise ValueError(
                "force is required for bending_moment."
            )

        if distance is None:
            raise ValueError(
                "distance is required for bending_moment."
            )

        result = force * distance

        return result

    # =====================================================
    # SHEAR FORCE
    # =====================================================

    elif operation == "shear_force":

        if force is None:
            raise ValueError(
                "force is required for shear_force."
            )

        result = force

        return result

    # =====================================================
    # INVALID OPERATION
    # =====================================================

    else:

        raise ValueError(
            f"Unsupported operation: {operation}"
        )