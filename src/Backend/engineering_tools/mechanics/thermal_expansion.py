from typing import Literal
from langchain_core.tools import tool


@tool
def thermal_expansion(
    operation: Literal[
        "linear_expansion",
        "thermal_strain",
        "dimensional_change",
    ],
    initial_length: float,
    thermal_expansion_coefficient: float,
    temperature_change: float,
    final_length: float | None = None,
) -> float:
    """
    Calculate dimensional changes caused by temperature changes.

    ---------------------------------------------------------
    1. LINEAR EXPANSION
    ---------------------------------------------------------

    Change in length:

        ΔL = α * L0 * ΔT

    where:

        ΔL = change in length [m]
        α  = coefficient of linear thermal expansion [1/K]
        L0 = original length [m]
        ΔT = temperature change [K or °C]

    ---------------------------------------------------------
    2. THERMAL STRAIN
    ---------------------------------------------------------

        ε_thermal = ΔL / L0

    Since:

        ΔL = α * L0 * ΔT

    then:

        ε_thermal = α * ΔT

    Thermal strain is dimensionless.

    ---------------------------------------------------------
    3. DIMENSIONAL CHANGE
    ---------------------------------------------------------

    Final dimension:

        Lf = L0 + ΔL

    Therefore:

        Lf = L0 * (1 + α*ΔT)

    If final_length is supplied, the tool instead calculates
    the dimensional change:

        ΔL = Lf - L0

    Units:

        initial_length -> m
        coefficient -> 1/K
        temperature_change -> K or °C
        final_length -> m

    Notes:

        - Temperature difference in °C and K has the same
          numerical value.
        - A positive temperature change produces expansion.
        - A negative temperature change produces contraction.
        - This assumes a constant coefficient of thermal
          expansion over the temperature range.
        - This is free thermal expansion; constrained thermal
          expansion can generate thermal stress.
    """

    # ---------------------------------------------------------
    # COMMON VALIDATION
    # ---------------------------------------------------------

    if initial_length <= 0:
        raise ValueError(
            "initial_length must be greater than zero."
        )

    if thermal_expansion_coefficient < 0:
        raise ValueError(
            "thermal_expansion_coefficient cannot be negative."
        )

    # ---------------------------------------------------------
    # LINEAR EXPANSION
    # ---------------------------------------------------------

    if operation == "linear_expansion":

        # ΔL = α * L0 * ΔT

        delta_length = (
            thermal_expansion_coefficient
            * initial_length
            * temperature_change
        )

        return delta_length

    # ---------------------------------------------------------
    # THERMAL STRAIN
    # ---------------------------------------------------------

    elif operation == "thermal_strain":

        # ε = α * ΔT

        thermal_strain_value = (
            thermal_expansion_coefficient
            * temperature_change
        )

        return thermal_strain_value

    # ---------------------------------------------------------
    # DIMENSIONAL CHANGE
    # ---------------------------------------------------------

    elif operation == "dimensional_change":

        if final_length is not None:

            if final_length < 0:
                raise ValueError(
                    "final_length cannot be negative."
                )

            # ΔL = Lf - L0

            return final_length - initial_length

        # Otherwise calculate final length from thermal expansion

        delta_length = (
            thermal_expansion_coefficient
            * initial_length
            * temperature_change
        )

        # Lf = L0 + ΔL

        return initial_length + delta_length

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )