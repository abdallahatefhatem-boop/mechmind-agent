from typing import Literal
from langchain_core.tools import tool


@tool
def thermodynamics(
    operation: Literal[
        "work",
        "heat",
        "internal_energy",
        "enthalpy",
        "efficiency",
    ],
    heat: float | None = None,
    work: float | None = None,
    pressure: float | None = None,
    volume_change: float | None = None,
    mass: float | None = None,
    specific_heat: float | None = None,
    temperature_change: float | None = None,
    internal_energy_initial: float | None = None,
    internal_energy_final: float | None = None,
    enthalpy_initial: float | None = None,
    enthalpy_final: float | None = None,
    efficiency_value: float | None = None,
    energy_input: float | None = None,
    energy_output: float | None = None,
) -> float:
    """
    Solve basic thermodynamic calculations.

    ---------------------------------------------------------
    SIGN CONVENTION
    ---------------------------------------------------------

    The First Law is written as:

        ΔU = Q - W

    where:

        ΔU = change in internal energy [J]
        Q  = heat added to the system [J]
        W  = work done BY the system [J]

    Therefore:

        Q = ΔU + W

        W = Q - ΔU

    Positive Q:
        Heat enters the system.

    Positive W:
        System performs work on the surroundings.

    ---------------------------------------------------------
    1. WORK
    ---------------------------------------------------------

    For constant pressure boundary work:

        W = P * ΔV

    where:

        P  = pressure [Pa]
        ΔV = volume change [m^3]

    Positive ΔV means expansion and positive work.

    ---------------------------------------------------------
    2. HEAT
    ---------------------------------------------------------

    First Law:

        Q = ΔU + W

    For a substance heated without phase change:

        Q = m * c * ΔT

    If sufficient information is provided, the tool uses:

        Q = m*c*ΔT

    Otherwise, when internal energy change and work
    are provided:

        Q = ΔU + W

    ---------------------------------------------------------
    3. INTERNAL ENERGY
    ---------------------------------------------------------

    First Law:

        ΔU = Q - W

    For a simple sensible-heating process:

        ΔU = m*c_v*ΔT

    Here `specific_heat` is treated as the appropriate
    specific heat for the supplied problem.

    ---------------------------------------------------------
    4. ENTHALPY
    ---------------------------------------------------------

        H = U + PV

    Therefore:

        ΔH = ΔU + Δ(PV)

    For constant pressure:

        ΔH = ΔU + P*ΔV

    For sensible heating using a specific heat:

        ΔH = m*c_p*ΔT

    ---------------------------------------------------------
    5. EFFICIENCY
    ---------------------------------------------------------

        efficiency = useful output / input

    Therefore:

        eta = E_out / E_in

    or, if efficiency is already known:

        E_out = eta * E_in

    Efficiency is returned as a decimal between 0 and 1.

    Units:

        pressure       -> Pa
        volume_change  -> m^3
        heat/work      -> J
        mass           -> kg
        specific_heat  -> J/(kg*K)
        temperature    -> K or deg C difference
        enthalpy       -> J
        internal energy -> J
    """

    # ---------------------------------------------------------
    # WORK
    # ---------------------------------------------------------

    if operation == "work":

        if pressure is None:
            raise ValueError(
                "pressure is required for work."
            )

        if volume_change is None:
            raise ValueError(
                "volume_change is required for work."
            )

        if pressure < 0:
            raise ValueError(
                "pressure cannot be negative."
            )

        # Constant-pressure boundary work:
        #
        # W = P * ΔV

        return pressure * volume_change

    # ---------------------------------------------------------
    # HEAT
    # ---------------------------------------------------------

    elif operation == "heat":

        # Method 1:
        # Q = m*c*ΔT

        if (
            mass is not None
            and specific_heat is not None
            and temperature_change is not None
        ):

            if mass <= 0:
                raise ValueError(
                    "mass must be greater than zero."
                )

            if specific_heat <= 0:
                raise ValueError(
                    "specific_heat must be greater than zero."
                )

            return (
                mass
                * specific_heat
                * temperature_change
            )

        # Method 2:
        # Q = ΔU + W

        if (
            internal_energy_initial is not None
            and internal_energy_final is not None
            and work is not None
        ):

            delta_u = (
                internal_energy_final
                - internal_energy_initial
            )

            return delta_u + work

        # Method 3:
        # If ΔU is directly supplied as `internal_energy_final`
        # and initial value is omitted, interpret final value
        # as the supplied energy change.

        if (
            internal_energy_final is not None
            and internal_energy_initial is None
            and work is not None
        ):

            return internal_energy_final + work

        raise ValueError(
            "heat requires either "
            "(mass, specific_heat, temperature_change) "
            "or "
            "(internal_energy_initial, internal_energy_final, work)."
        )

    # ---------------------------------------------------------
    # INTERNAL ENERGY
    # ---------------------------------------------------------

    elif operation == "internal_energy":

        # Method 1:
        # ΔU = m*c*ΔT

        if (
            mass is not None
            and specific_heat is not None
            and temperature_change is not None
        ):

            if mass <= 0:
                raise ValueError(
                    "mass must be greater than zero."
                )

            if specific_heat <= 0:
                raise ValueError(
                    "specific_heat must be greater than zero."
                )

            return (
                mass
                * specific_heat
                * temperature_change
            )

        # Method 2:
        # ΔU = Q - W

        if heat is not None and work is not None:

            return heat - work

        # Method 3:
        # Calculate ΔU from initial/final values

        if (
            internal_energy_initial is not None
            and internal_energy_final is not None
        ):

            return (
                internal_energy_final
                - internal_energy_initial
            )

        raise ValueError(
            "internal_energy requires either "
            "(mass, specific_heat, temperature_change), "
            "(heat, work), or "
            "(internal_energy_initial, internal_energy_final)."
        )

    # ---------------------------------------------------------
    # ENTHALPY
    # ---------------------------------------------------------

    elif operation == "enthalpy":

        # Method 1:
        # ΔH = m*c*ΔT

        if (
            mass is not None
            and specific_heat is not None
            and temperature_change is not None
        ):

            if mass <= 0:
                raise ValueError(
                    "mass must be greater than zero."
                )

            if specific_heat <= 0:
                raise ValueError(
                    "specific_heat must be greater than zero."
                )

            return (
                mass
                * specific_heat
                * temperature_change
            )

        # Method 2:
        # ΔH = ΔU + P*ΔV

        if (
            internal_energy_initial is not None
            and internal_energy_final is not None
            and pressure is not None
            and volume_change is not None
        ):

            delta_u = (
                internal_energy_final
                - internal_energy_initial
            )

            return (
                delta_u
                + pressure * volume_change
            )

        # Method 3:
        # ΔH = H_final - H_initial

        if (
            enthalpy_initial is not None
            and enthalpy_final is not None
        ):

            return (
                enthalpy_final
                - enthalpy_initial
            )

        raise ValueError(
            "enthalpy requires either "
            "(mass, specific_heat, temperature_change), "
            "(internal energies, pressure, volume_change), "
            "or (enthalpy_initial, enthalpy_final)."
        )

    # ---------------------------------------------------------
    # EFFICIENCY
    # ---------------------------------------------------------

    elif operation == "efficiency":

        # Calculate efficiency:
        #
        # eta = output / input

        if (
            energy_output is not None
            and energy_input is not None
        ):

            if energy_input <= 0:
                raise ValueError(
                    "energy_input must be greater than zero."
                )

            if energy_output < 0:
                raise ValueError(
                    "energy_output cannot be negative."
                )

            efficiency_result = (
                energy_output / energy_input
            )

            if efficiency_result > 1:
                raise ValueError(
                    "Calculated efficiency cannot exceed 1."
                )

            return efficiency_result

        # Calculate output from known efficiency:
        #
        # E_out = eta * E_in

        if (
            efficiency_value is not None
            and energy_input is not None
        ):

            if not 0 < efficiency_value <= 1:
                raise ValueError(
                    "efficiency_value must be greater than 0 "
                    "and less than or equal to 1."
                )

            if energy_input < 0:
                raise ValueError(
                    "energy_input cannot be negative."
                )

            return (
                efficiency_value
                * energy_input
            )

        raise ValueError(
            "efficiency requires either "
            "(energy_output, energy_input) "
            "or "
            "(efficiency_value, energy_input)."
        )

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )