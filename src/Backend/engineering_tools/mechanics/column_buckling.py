from typing import Literal
from math import pi
from langchain_core.tools import tool


@tool
def column_buckling(
    operation: Literal[
        "critical_load",
        "buckling_stress",
    ],
    elasticity_modulus: float,
    moment_of_inertia: float,
    length: float,
    effective_length_factor: float,
    area: float | None = None,
) -> float:
    """
    Calculate column buckling using Euler's buckling equation.

    Euler critical buckling load:

        P_cr = pi^2 * E * I / (K * L)^2

    Critical buckling stress:

        sigma_cr = P_cr / A

    Supported operations:

        critical_load:
            Calculate the critical Euler buckling load.

        buckling_stress:
            Calculate the critical Euler buckling stress.

    Parameters:
        operation:
            "critical_load" or "buckling_stress"

        elasticity_modulus:
            Young's modulus E [Pa].

        moment_of_inertia:
            Least second moment of area I [m^4].

        length:
            Actual unsupported column length L [m].

        effective_length_factor:
            Effective length factor K.

            Common values:
                pinned-pinned   = 1.0
                fixed-fixed     = 0.5
                fixed-pinned    ≈ 0.699
                fixed-free      = 2.0

        area:
            Cross-sectional area A [m^2].
            Required only for buckling_stress.

    Returns:
        Critical load in Newtons for "critical_load".

        Buckling stress in Pascals for "buckling_stress".

    Assumptions:
        - Euler elastic buckling theory.
        - Straight, slender column.
        - Homogeneous material.
        - Idealized boundary conditions.
        - Buckling occurs about the weakest axis.
    """

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if elasticity_modulus <= 0:
        raise ValueError(
            "Elasticity modulus must be greater than zero."
        )

    if moment_of_inertia <= 0:
        raise ValueError(
            "Moment of inertia must be greater than zero."
        )

    if length <= 0:
        raise ValueError(
            "Column length must be greater than zero."
        )

    if effective_length_factor <= 0:
        raise ValueError(
            "Effective length factor K must be greater than zero."
        )

    # =====================================================
    # EULER CRITICAL BUCKLING LOAD
    # =====================================================

    critical_load = (
        pi**2
        * elasticity_modulus
        * moment_of_inertia
        / (
            effective_length_factor * length
        )**2
    )

    # =====================================================
    # CRITICAL LOAD
    # =====================================================

    if operation == "critical_load":
        return critical_load

    # =====================================================
    # BUCKLING STRESS
    # =====================================================

    if operation == "buckling_stress":

        if area is None:
            raise ValueError(
                "area is required for buckling_stress."
            )

        if area <= 0:
            raise ValueError(
                "Cross-sectional area must be greater than zero."
            )

        buckling_stress = critical_load / area

        return buckling_stress

    # =====================================================
    # INVALID OPERATION
    # =====================================================

    raise ValueError(
        f"Unsupported operation: {operation}"
    )