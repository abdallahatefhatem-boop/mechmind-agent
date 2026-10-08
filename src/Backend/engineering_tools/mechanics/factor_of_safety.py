from typing import Literal
from langchain_core.tools import tool


@tool
def factor_of_safety(
    operation: Literal[
        "yield_strength",
        "ultimate_strength",
        "applied_stress",
    ],
    strength: float,
    applied_stress: float,
) -> float:
    """
    Calculate the factor of safety for an engineering component.

    The factor of safety is calculated as:

        FoS = Material Strength / Applied Stress

    Operations:
        yield_strength:
            Calculate factor of safety using yield strength.

        ultimate_strength:
            Calculate factor of safety using ultimate strength.

        applied_stress:
            Calculate factor of safety using the provided
            material strength and applied stress.

    Parameters:
        operation:
            Type of factor-of-safety calculation.

        strength:
            Material strength, such as yield strength or
            ultimate strength.

        applied_stress:
            Stress applied to the engineering component.

    Important:
        strength and applied_stress must use the same units.

    Examples:
        Yield-based FoS:
            factor_of_safety(
                operation="yield_strength",
                strength=250,
                applied_stress=100
            )

        Ultimate-based FoS:
            factor_of_safety(
                operation="ultimate_strength",
                strength=400,
                applied_stress=200
            )
    """

    # =========================
    # Input Validation
    # =========================

    if strength <= 0:
        raise ValueError(
            "Material strength must be greater than zero."
        )

    if applied_stress <= 0:
        raise ValueError(
            "Applied stress must be greater than zero."
        )

    # =========================
    # Factor of Safety
    # =========================

    if operation == "yield_strength":
        result = strength / applied_stress

    elif operation == "ultimate_strength":
        result = strength / applied_stress

    elif operation == "applied_stress":
        result = strength / applied_stress

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    return result