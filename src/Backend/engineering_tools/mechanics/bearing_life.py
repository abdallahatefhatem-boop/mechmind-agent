from typing import Literal
from langchain_core.tools import tool


@tool
def bearing_life(
    operation: Literal[
        "bearing_life",
        "equivalent_load",
        "dynamic_load_rating",
    ],
    dynamic_load_rating_value: float | None = None,
    equivalent_load_value: float | None = None,
    radial_load: float | None = None,
    axial_load: float | None = None,
    radial_factor: float = 1.0,
    axial_factor: float = 0.0,
    life_million_revolutions: float | None = None,
    speed_rpm: float | None = None,
    bearing_type: Literal[
        "ball",
        "roller",
    ] = "ball",
) -> float:
    """
    Calculate bearing equivalent load, dynamic load rating,
    or basic L10 bearing life.

    ---------------------------------------------------------
    1. BEARING LIFE
    ---------------------------------------------------------

    Basic rating life:

        L10 = (C / P)^p

    where:

        L10 = bearing life in million revolutions
        C   = basic dynamic load rating
        P   = equivalent dynamic bearing load
        p   = life exponent

    For ball bearings:

        p = 3

    For roller bearings:

        p = 10/3

    If speed is provided, life can also be converted to hours:

        L10_hours = (L10 * 1,000,000) / (60 * RPM)

    ---------------------------------------------------------
    2. EQUIVALENT LOAD
    ---------------------------------------------------------

    Simplified equivalent dynamic load:

        P = X * Fr + Y * Fa

    where:

        Fr = radial load
        Fa = axial load
        X  = radial load factor
        Y  = axial load factor

    This implementation uses user-supplied X and Y.

    ---------------------------------------------------------
    3. DYNAMIC LOAD RATING
    ---------------------------------------------------------

    Rearranging:

        L10 = (C / P)^p

    gives:

        C = P * L10^(1/p)

    ---------------------------------------------------------
    Units:
        Loads and dynamic load rating must use the same units.

        Example:
            C  = N
            Fr = N
            Fa = N
            P  = N

        Speed is RPM.

    Important:
        Real bearing selection normally requires manufacturer
        factors X and Y, static load rating, reliability,
        lubrication, temperature, contamination, and other
        application factors.
    """

    # ---------------------------------------------------------
    # DETERMINE LIFE EXPONENT
    # ---------------------------------------------------------

    if bearing_type == "ball":
        p = 3.0

    elif bearing_type == "roller":
        p = 10.0 / 3.0

    else:
        raise ValueError(
            f"Unsupported bearing type: {bearing_type}"
        )

    # ---------------------------------------------------------
    # BEARING LIFE
    # ---------------------------------------------------------

    if operation == "bearing_life":

        if dynamic_load_rating_value is None:
            raise ValueError(
                "dynamic_load_rating_value is required "
                "for bearing_life."
            )

        if equivalent_load_value is None:
            raise ValueError(
                "equivalent_load_value is required "
                "for bearing_life."
            )

        if dynamic_load_rating_value <= 0:
            raise ValueError(
                "Dynamic load rating must be greater than zero."
            )

        if equivalent_load_value <= 0:
            raise ValueError(
                "Equivalent load must be greater than zero."
            )

        # L10 in million revolutions
        life_million_revolutions = (
            dynamic_load_rating_value
            / equivalent_load_value
        ) ** p

        # If RPM is supplied, return life in hours.
        if speed_rpm is not None:

            if speed_rpm <= 0:
                raise ValueError(
                    "speed_rpm must be greater than zero."
                )

            life_hours = (
                life_million_revolutions * 1_000_000
            ) / (
                60 * speed_rpm
            )

            return life_hours

        return life_million_revolutions

    # ---------------------------------------------------------
    # EQUIVALENT LOAD
    # ---------------------------------------------------------

    elif operation == "equivalent_load":

        if radial_load is None:
            raise ValueError(
                "radial_load is required for equivalent_load."
            )

        if axial_load is None:
            raise ValueError(
                "axial_load is required for equivalent_load."
            )

        if radial_load < 0:
            raise ValueError(
                "radial_load cannot be negative."
            )

        if axial_load < 0:
            raise ValueError(
                "axial_load cannot be negative."
            )

        if radial_factor < 0:
            raise ValueError(
                "radial_factor cannot be negative."
            )

        if axial_factor < 0:
            raise ValueError(
                "axial_factor cannot be negative."
            )

        # P = X*Fr + Y*Fa
        equivalent_load = (
            radial_factor * radial_load
            + axial_factor * axial_load
        )

        if equivalent_load <= 0:
            raise ValueError(
                "Equivalent load must be greater than zero."
            )

        return equivalent_load

    # ---------------------------------------------------------
    # DYNAMIC LOAD RATING
    # ---------------------------------------------------------

    elif operation == "dynamic_load_rating":

        if equivalent_load_value is None:
            raise ValueError(
                "equivalent_load_value is required "
                "for dynamic_load_rating."
            )

        if life_million_revolutions is None:
            raise ValueError(
                "life_million_revolutions is required "
                "for dynamic_load_rating."
            )

        if equivalent_load_value <= 0:
            raise ValueError(
                "Equivalent load must be greater than zero."
            )

        if life_million_revolutions <= 0:
            raise ValueError(
                "Bearing life must be greater than zero."
            )

        # C = P * L10^(1/p)
        dynamic_load_rating = (
            equivalent_load_value
            * life_million_revolutions ** (1.0 / p)
        )

        return dynamic_load_rating

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )