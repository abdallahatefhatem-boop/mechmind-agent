from typing import Literal
from math import pi, sqrt
from langchain_core.tools import tool


@tool
def shaft_design(
    operation: Literal[
        "shaft_diameter",
        "torsional_stress",
        "shear_stress",
        "factor_of_safety",
    ],
    torque: float | None = None,
    bending_moment: float | None = None,
    diameter: float | None = None,
    allowable_stress: float | None = None,
    yield_strength: float | None = None,
    transverse_force: float | None = None,
    area: float | None = None,
) -> float:
    """
    Design and analyze a solid circular shaft under torque and bending loads.

    Supported operations:

    1. shaft_diameter
       Calculate required shaft diameter considering combined bending
       and torsional loading.

       Bending stress:
           sigma = 32*M / (pi*d^3)

       Torsional shear stress:
           tau = 16*T / (pi*d^3)

       Von Mises equivalent stress:
           sigma_vm = sqrt(sigma^2 + 3*tau^2)

       Required diameter:
           d = [
               (16 / (pi * allowable_stress))
               * sqrt(4*M^2 + 3*T^2)
           ]^(1/3)

       Requires:
           torque
           bending_moment
           allowable_stress

    2. torsional_stress
       Calculate torsional shear stress in a solid circular shaft.

           tau = 16*T / (pi*d^3)

       Requires:
           torque
           diameter

    3. shear_stress
       Calculate combined transverse and torsional shear stress.

       Torsional shear:
           tau_t = 16*T / (pi*d^3)

       Average transverse shear:
           tau_v = F / A

       Conservative combined shear:
           tau_total = tau_t + tau_v

       Requires:
           torque
           diameter
           transverse_force
           area

    4. factor_of_safety
       Calculate factor of safety using Von Mises stress.

           sigma_b = 32*M / (pi*d^3)

           tau_t = 16*T / (pi*d^3)

           sigma_vm = sqrt(sigma_b^2 + 3*tau_t^2)

           FoS = yield_strength / sigma_vm

       Requires:
           torque
           bending_moment
           diameter
           yield_strength

    Important:
        All quantities must use a consistent unit system.

        Example:
            torque     -> N*m
            bending    -> N*m
            diameter   -> m
            stress     -> Pa
            yield      -> Pa

        This implementation assumes a solid circular shaft.
    """

    # ---------------------------------------------------------
    # SHAFT DIAMETER
    # ---------------------------------------------------------
    if operation == "shaft_diameter":

        if torque is None:
            raise ValueError(
                "torque is required for shaft_diameter."
            )

        if bending_moment is None:
            raise ValueError(
                "bending_moment is required for shaft_diameter."
            )

        if allowable_stress is None:
            raise ValueError(
                "allowable_stress is required for shaft_diameter."
            )

        if torque < 0:
            raise ValueError(
                "Torque cannot be negative."
            )

        if bending_moment < 0:
            raise ValueError(
                "Bending moment cannot be negative."
            )

        if allowable_stress <= 0:
            raise ValueError(
                "Allowable stress must be greater than zero."
            )

        # Required diameter for combined bending + torsion
        diameter_required = (
            (
                16
                * sqrt(
                    4 * bending_moment**2
                    + 3 * torque**2
                )
            )
            / (pi * allowable_stress)
        ) ** (1 / 3)

        return diameter_required

    # ---------------------------------------------------------
    # TORSIONAL STRESS
    # ---------------------------------------------------------
    elif operation == "torsional_stress":

        if torque is None:
            raise ValueError(
                "torque is required for torsional_stress."
            )

        if diameter is None:
            raise ValueError(
                "diameter is required for torsional_stress."
            )

        if torque < 0:
            raise ValueError(
                "Torque cannot be negative."
            )

        if diameter <= 0:
            raise ValueError(
                "Diameter must be greater than zero."
            )

        # Solid circular shaft:
        #
        # tau = 16T / (pi*d^3)

        torsional_stress = (
            16 * torque
        ) / (
            pi * diameter**3
        )

        return torsional_stress

    # ---------------------------------------------------------
    # SHEAR STRESS
    # ---------------------------------------------------------
    elif operation == "shear_stress":

        if torque is None:
            raise ValueError(
                "torque is required for shear_stress."
            )

        if diameter is None:
            raise ValueError(
                "diameter is required for shear_stress."
            )

        if transverse_force is None:
            raise ValueError(
                "transverse_force is required for shear_stress."
            )

        if area is None:
            raise ValueError(
                "area is required for shear_stress."
            )

        if diameter <= 0:
            raise ValueError(
                "Diameter must be greater than zero."
            )

        if area <= 0:
            raise ValueError(
                "Area must be greater than zero."
            )

        # Torsional shear stress
        torsional_shear = (
            16 * abs(torque)
        ) / (
            pi * diameter**3
        )

        # Average transverse shear stress
        transverse_shear = (
            abs(transverse_force) / area
        )

        # Conservative combination
        total_shear = (
            torsional_shear
            + transverse_shear
        )

        return total_shear

    # ---------------------------------------------------------
    # FACTOR OF SAFETY
    # ---------------------------------------------------------
    elif operation == "factor_of_safety":

        if torque is None:
            raise ValueError(
                "torque is required for factor_of_safety."
            )

        if bending_moment is None:
            raise ValueError(
                "bending_moment is required for factor_of_safety."
            )

        if diameter is None:
            raise ValueError(
                "diameter is required for factor_of_safety."
            )

        if yield_strength is None:
            raise ValueError(
                "yield_strength is required for factor_of_safety."
            )

        if diameter <= 0:
            raise ValueError(
                "Diameter must be greater than zero."
            )

        if yield_strength <= 0:
            raise ValueError(
                "Yield strength must be greater than zero."
            )

        # Bending normal stress
        bending_stress = (
            32 * abs(bending_moment)
        ) / (
            pi * diameter**3
        )

        # Torsional shear stress
        torsional_shear = (
            16 * abs(torque)
        ) / (
            pi * diameter**3
        )

        # Von Mises equivalent stress
        von_mises_stress = sqrt(
            bending_stress**2
            + 3 * torsional_shear**2
        )

        # Factor of safety
        fos = (
            yield_strength
            / von_mises_stress
        )

        return fos

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )