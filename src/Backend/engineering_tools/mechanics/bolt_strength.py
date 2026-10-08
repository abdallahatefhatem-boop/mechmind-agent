from typing import Literal
from math import pi
from langchain_core.tools import tool


@tool
def bolt_strength(
    operation: Literal[
        "tensile_stress",
        "shear_stress",
        "bolt_strength",
        "preload",
    ],
    force: float | None = None,
    diameter: float | None = None,
    tensile_area: float | None = None,
    shear_area: float | None = None,
    tensile_strength: float | None = None,
    yield_strength: float | None = None,
    preload_factor: float = 0.7,
    proof_strength: float | None = None,
) -> float:
    """
    Calculate bolt tensile stress, shear stress, bolt strength,
    or recommended preload.

    ---------------------------------------------------------
    1. TENSILE STRESS
    ---------------------------------------------------------

    Tensile stress:

        sigma = F / A_t

    where:

        F   = tensile force [N]
        A_t = tensile stress area [m^2]

    If tensile_area is not provided, the tool approximates the
    area using the nominal bolt diameter:

        A = pi*d^2 / 4

    Note:
        For threaded bolts, the actual tensile stress area is
        smaller than the nominal shank area. For accurate bolt
        calculations, provide tensile_area.

    ---------------------------------------------------------
    2. SHEAR STRESS
    ---------------------------------------------------------

    Average shear stress:

        tau = F / A_s

    where:

        F   = shear force [N]
        A_s = shear area [m^2]

    If shear_area is not provided, the tool approximates:

        A_s = pi*d^2 / 4

    ---------------------------------------------------------
    3. BOLT STRENGTH
    ---------------------------------------------------------

    Calculate the maximum tensile load based on tensile strength:

        F_max = sigma_u * A_t

    If yield_strength is provided, the yield load is also
    calculated conceptually as:

        F_y = sigma_y * A_t

    This operation returns the tensile load corresponding to
    tensile_strength.

    ---------------------------------------------------------
    4. PRELOAD
    ---------------------------------------------------------

    Recommended preload:

        F_preload = k * F_proof

    where:

        k = preload factor
        F_proof = proof load

    If proof_strength is provided:

        F_proof = proof_strength * A_t

    Therefore:

        F_preload = preload_factor * proof_strength * A_t

    If proof_strength is not supplied, tensile_strength is used
    as a fallback.

    Typical preload factor:
        0.7

    Units:
        Force -> N
        Diameter -> m
        Area -> m^2
        Stress/strength -> Pa

    Important:
        This is a basic fastener-strength calculator.
        Real bolt design may require thread geometry, bearing
        stress, joint stiffness, fatigue, tightening torque,
        friction, eccentric loading, and standards such as
        ISO 898-1 or ASME specifications.
    """

    # ---------------------------------------------------------
    # TENSILE STRESS
    # ---------------------------------------------------------

    if operation == "tensile_stress":

        if force is None:
            raise ValueError(
                "force is required for tensile_stress."
            )

        if force < 0:
            raise ValueError(
                "force cannot be negative."
            )

        # Use provided tensile stress area if available.
        if tensile_area is not None:

            if tensile_area <= 0:
                raise ValueError(
                    "tensile_area must be greater than zero."
                )

            area = tensile_area

        else:

            if diameter is None:
                raise ValueError(
                    "Either tensile_area or diameter is required "
                    "for tensile_stress."
                )

            if diameter <= 0:
                raise ValueError(
                    "diameter must be greater than zero."
                )

            # Nominal circular area
            area = pi * diameter**2 / 4

        # sigma = F/A
        return force / area

    # ---------------------------------------------------------
    # SHEAR STRESS
    # ---------------------------------------------------------

    elif operation == "shear_stress":

        if force is None:
            raise ValueError(
                "force is required for shear_stress."
            )

        if force < 0:
            raise ValueError(
                "force cannot be negative."
            )

        if shear_area is not None:

            if shear_area <= 0:
                raise ValueError(
                    "shear_area must be greater than zero."
                )

            area = shear_area

        else:

            if diameter is None:
                raise ValueError(
                    "Either shear_area or diameter is required "
                    "for shear_stress."
                )

            if diameter <= 0:
                raise ValueError(
                    "diameter must be greater than zero."
                )

            area = pi * diameter**2 / 4

        # tau = F/A
        return force / area

    # ---------------------------------------------------------
    # BOLT STRENGTH
    # ---------------------------------------------------------

    elif operation == "bolt_strength":

        if tensile_strength is None:
            raise ValueError(
                "tensile_strength is required for bolt_strength."
            )

        if tensile_strength <= 0:
            raise ValueError(
                "tensile_strength must be greater than zero."
            )

        if tensile_area is not None:

            if tensile_area <= 0:
                raise ValueError(
                    "tensile_area must be greater than zero."
                )

            area = tensile_area

        else:

            if diameter is None:
                raise ValueError(
                    "Either tensile_area or diameter is required "
                    "for bolt_strength."
                )

            if diameter <= 0:
                raise ValueError(
                    "diameter must be greater than zero."
                )

            area = pi * diameter**2 / 4

        # Maximum tensile load:
        #
        # Fmax = sigma_u * A
        return tensile_strength * area

    # ---------------------------------------------------------
    # PRELOAD
    # ---------------------------------------------------------

    elif operation == "preload":

        if preload_factor <= 0 or preload_factor > 1:
            raise ValueError(
                "preload_factor must be greater than 0 "
                "and less than or equal to 1."
            )

        # Determine bolt area
        if tensile_area is not None:

            if tensile_area <= 0:
                raise ValueError(
                    "tensile_area must be greater than zero."
                )

            area = tensile_area

        else:

            if diameter is None:
                raise ValueError(
                    "Either tensile_area or diameter is required "
                    "for preload."
                )

            if diameter <= 0:
                raise ValueError(
                    "diameter must be greater than zero."
                )

            area = pi * diameter**2 / 4

        # Determine proof strength
        if proof_strength is not None:

            if proof_strength <= 0:
                raise ValueError(
                    "proof_strength must be greater than zero."
                )

            strength = proof_strength

        elif tensile_strength is not None:

            if tensile_strength <= 0:
                raise ValueError(
                    "tensile_strength must be greater than zero."
                )

            strength = tensile_strength

        else:
            raise ValueError(
                "proof_strength or tensile_strength is required "
                "for preload."
            )

        # Proof load:
        #
        # Fproof = proof_strength * A
        #
        # Preload:
        #
        # Fpreload = preload_factor * Fproof

        proof_load = strength * area

        return preload_factor * proof_load

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )