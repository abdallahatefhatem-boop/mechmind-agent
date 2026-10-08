from typing import Literal
from langchain_core.tools import tool


@tool
def beam_deflection(
    operation: Literal[
        "deflection",
        "slope",
    ],
    load_type: Literal[
        "point_load_center",
        "point_load_end",
        "uniform_load",
    ],
    load: float,
    length: float,
    elasticity_modulus: float,
    moment_of_inertia: float,
) -> float:
    """
    Calculate beam deflection or slope for common beam loading cases.

    Supported operations:
        - deflection
        - slope

    Supported load types:
        - point_load_center:
            Simply supported beam with a point load at the center.

        - point_load_end:
            Cantilever beam with a point load at the free end.

        - uniform_load:
            Simply supported beam with a uniformly distributed load
            over the entire beam.

    Parameters:
        operation:
            "deflection" or "slope"

        load_type:
            Type and location of beam loading.

        load:
            Applied load.

            For point_load_center:
                Force P [N]

            For point_load_end:
                Force P [N]

            For uniform_load:
                Distributed load w [N/m]

        length:
            Beam length L [m]

        elasticity_modulus:
            Young's modulus E [Pa]

        moment_of_inertia:
            Second moment of area I [m^4]

    Returns:
        Deflection in meters for "deflection".
        Slope in radians for "slope".

    Formulas:

        Simply supported beam + center point load:

            δ = P L^3 / (48 E I)

            θ = P L^2 / (16 E I)

        Cantilever + end point load:

            δ = P L^3 / (3 E I)

            θ = P L^2 / (2 E I)

        Simply supported beam + uniform load:

            δ = 5 w L^4 / (384 E I)

            θ = w L^3 / (24 E I)
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    if load <= 0:
        raise ValueError(
            "Load must be greater than zero."
        )

    if length <= 0:
        raise ValueError(
            "Beam length must be greater than zero."
        )

    if elasticity_modulus <= 0:
        raise ValueError(
            "Elasticity modulus must be greater than zero."
        )

    if moment_of_inertia <= 0:
        raise ValueError(
            "Moment of inertia must be greater than zero."
        )

    # =====================================================
    # SIMPLY SUPPORTED + CENTER POINT LOAD
    # =====================================================

    if load_type == "point_load_center":

        if operation == "deflection":

            result = (
                load * length**3
            ) / (
                48
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

        elif operation == "slope":

            result = (
                load * length**2
            ) / (
                16
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

    # =====================================================
    # CANTILEVER + END POINT LOAD
    # =====================================================

    elif load_type == "point_load_end":

        if operation == "deflection":

            result = (
                load * length**3
            ) / (
                3
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

        elif operation == "slope":

            result = (
                load * length**2
            ) / (
                2
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

    # =====================================================
    # SIMPLY SUPPORTED + UNIFORM LOAD
    # =====================================================

    elif load_type == "uniform_load":

        if operation == "deflection":

            result = (
                5
                * load
                * length**4
            ) / (
                384
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

        elif operation == "slope":

            result = (
                load
                * length**3
            ) / (
                24
                * elasticity_modulus
                * moment_of_inertia
            )

            return result

    # =====================================================
    # INVALID OPERATION
    # =====================================================

    raise ValueError(
        f"Unsupported combination: "
        f"operation={operation}, "
        f"load_type={load_type}"
    )