from typing import Literal
from langchain_core.tools import tool


@tool
def fatigue_life(
    operation: Literal[
        "fatigue_life",
        "stress_amplitude",
        "endurance_limit",
    ],
    stress_amplitude_value: float | None = None,
    cycles: float | None = None,
    fatigue_strength_coefficient: float | None = None,
    fatigue_exponent: float | None = None,
    endurance_limit_value: float | None = None,
) -> float:
    """
    Estimate fatigue behavior using an S-N Basquin model.

    Basquin equation:

        sigma_a = sigma_f' * (2 * N_f)^b

    where:

        sigma_a = stress amplitude
        sigma_f' = fatigue strength coefficient
        b = fatigue strength exponent
        N_f = cycles to failure

    Supported operations:

        fatigue_life:
            Calculate cycles to failure from stress amplitude.

        stress_amplitude:
            Calculate stress amplitude for a given number of cycles.

        endurance_limit:
            Return the specified material endurance limit.

    Parameters:

        operation:
            Type of fatigue calculation.

        stress_amplitude_value:
            Stress amplitude sigma_a.

        cycles:
            Number of cycles N_f.

        fatigue_strength_coefficient:
            Fatigue strength coefficient sigma_f'.

        fatigue_exponent:
            Basquin exponent b.
            Usually negative.

        endurance_limit_value:
            Material endurance limit.
            Required for the endurance_limit operation.

    Important:

        All stress quantities must use the same units.

        The Basquin model is an approximation and is mainly
        appropriate for high-cycle fatigue behavior.

    Returns:

        fatigue_life:
            Number of cycles to failure.

        stress_amplitude:
            Stress amplitude.

        endurance_limit:
            Endurance limit.
    """

    # =====================================================
    # ENDURANCE LIMIT
    # =====================================================

    if operation == "endurance_limit":

        if endurance_limit_value is None:
            raise ValueError(
                "endurance_limit_value is required "
                "for endurance_limit."
            )

        if endurance_limit_value <= 0:
            raise ValueError(
                "Endurance limit must be greater than zero."
            )

        return endurance_limit_value

    # =====================================================
    # VALIDATION FOR BASQUIN MODEL
    # =====================================================

    if fatigue_strength_coefficient is None:
        raise ValueError(
            "fatigue_strength_coefficient is required."
        )

    if fatigue_exponent is None:
        raise ValueError(
            "fatigue_exponent is required."
        )

    if fatigue_strength_coefficient <= 0:
        raise ValueError(
            "Fatigue strength coefficient must be "
            "greater than zero."
        )

    if fatigue_exponent >= 0:
        raise ValueError(
            "Fatigue exponent must normally be negative "
            "for the Basquin model."
        )

    # =====================================================
    # FATIGUE LIFE
    # =====================================================

    if operation == "fatigue_life":

        if stress_amplitude_value is None:
            raise ValueError(
                "stress_amplitude_value is required "
                "for fatigue_life."
            )

        if stress_amplitude_value <= 0:
            raise ValueError(
                "Stress amplitude must be greater than zero."
            )

        # sigma_a = sigma_f' * (2N)^b
        #
        # 2N = (sigma_a / sigma_f')^(1/b)
        #
        # N = 0.5 * (...)^(1/b)

        cycles = (
            0.5
            * (
                stress_amplitude_value
                / fatigue_strength_coefficient
            )
            ** (1 / fatigue_exponent)
        )

        return cycles

    # =====================================================
    # STRESS AMPLITUDE
    # =====================================================

    if operation == "stress_amplitude":

        if cycles is None:
            raise ValueError(
                "cycles is required for stress_amplitude."
            )

        if cycles <= 0:
            raise ValueError(
                "Cycles must be greater than zero."
            )

        stress_amplitude = (
            fatigue_strength_coefficient
            * (2 * cycles)
            ** fatigue_exponent
        )

        return stress_amplitude

    # =====================================================
    # INVALID OPERATION
    # =====================================================

    raise ValueError(
        f"Unsupported operation: {operation}"
    )