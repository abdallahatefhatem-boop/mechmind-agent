from typing import Literal
from math import pi
from langchain_core.tools import tool


@tool
def gear_design(
    operation: Literal[
        "gear_ratio",
        "output_speed",
        "output_torque",
        "power",
    ],
    input_speed: float | None = None,
    output_speed_value: float | None = None,
    input_torque: float | None = None,
    output_torque_value: float | None = None,
    input_teeth: int | None = None,
    output_teeth: int | None = None,
    efficiency: float = 1.0,
) -> float:
    """
    Calculate gear ratio, output speed, output torque, or mechanical power.

    Gear ratio:
        GR = N_output / N_input

    For an ideal gear pair:

        n_output = n_input / GR

        T_output = T_input * GR

    With efficiency:

        T_output = T_input * GR * efficiency

    Mechanical power:

        P = T * omega

    where:

        omega = 2*pi*n / 60

    Therefore:

        P = T * 2*pi*n / 60

    Inputs:
        input_speed:
            Input shaft speed in RPM.

        output_speed_value:
            Output shaft speed in RPM.
            Used when calculating gear ratio.

        input_torque:
            Input torque in N*m.

        output_torque_value:
            Output torque in N*m.
            Used when calculating gear ratio from torque.

        input_teeth:
            Number of teeth on the driving/input gear.

        output_teeth:
            Number of teeth on the driven/output gear.

        efficiency:
            Gear transmission efficiency from 0 to 1.
            Example:
                0.95 = 95% efficiency.

    Notes:
        - All speeds are RPM.
        - Torque is N*m.
        - Power is returned in Watts.
        - For gear_ratio, teeth are preferred because they directly
          determine the ratio.
        - This tool assumes two externally meshing gears.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if efficiency <= 0 or efficiency > 1:
        raise ValueError(
            "Efficiency must be greater than 0 and less than or equal to 1."
        )

    # ---------------------------------------------------------
    # GEAR RATIO
    # ---------------------------------------------------------

    if operation == "gear_ratio":

        # Preferred method: tooth counts
        if input_teeth is not None and output_teeth is not None:

            if input_teeth <= 0:
                raise ValueError(
                    "input_teeth must be greater than zero."
                )

            if output_teeth <= 0:
                raise ValueError(
                    "output_teeth must be greater than zero."
                )

            return output_teeth / input_teeth

        # Alternative: calculate ratio from speeds
        if (
            input_speed is not None
            and output_speed_value is not None
        ):

            if input_speed <= 0:
                raise ValueError(
                    "input_speed must be greater than zero."
                )

            if output_speed_value <= 0:
                raise ValueError(
                    "output_speed_value must be greater than zero."
                )

            return input_speed / output_speed_value

        # Alternative: calculate ratio from torques
        if (
            input_torque is not None
            and output_torque_value is not None
        ):

            if input_torque <= 0:
                raise ValueError(
                    "input_torque must be greater than zero."
                )

            if output_torque_value <= 0:
                raise ValueError(
                    "output_torque_value must be greater than zero."
                )

            return output_torque_value / (
                input_torque * efficiency
            )

        raise ValueError(
            "gear_ratio requires either "
            "(input_teeth and output_teeth), "
            "(input_speed and output_speed_value), "
            "or (input_torque and output_torque_value)."
        )

    # ---------------------------------------------------------
    # OUTPUT SPEED
    # ---------------------------------------------------------

    elif operation == "output_speed":

        if input_speed is None:
            raise ValueError(
                "input_speed is required for output_speed."
            )

        if input_teeth is None:
            raise ValueError(
                "input_teeth is required for output_speed."
            )

        if output_teeth is None:
            raise ValueError(
                "output_teeth is required for output_speed."
            )

        if input_speed <= 0:
            raise ValueError(
                "input_speed must be greater than zero."
            )

        if input_teeth <= 0:
            raise ValueError(
                "input_teeth must be greater than zero."
            )

        if output_teeth <= 0:
            raise ValueError(
                "output_teeth must be greater than zero."
            )

        # Gear ratio
        gear_ratio = output_teeth / input_teeth

        # Output speed
        #
        # n_out = n_in / GR

        return input_speed / gear_ratio

    # ---------------------------------------------------------
    # OUTPUT TORQUE
    # ---------------------------------------------------------

    elif operation == "output_torque":

        if input_torque is None:
            raise ValueError(
                "input_torque is required for output_torque."
            )

        if input_teeth is None:
            raise ValueError(
                "input_teeth is required for output_torque."
            )

        if output_teeth is None:
            raise ValueError(
                "output_teeth is required for output_torque."
            )

        if input_torque <= 0:
            raise ValueError(
                "input_torque must be greater than zero."
            )

        if input_teeth <= 0:
            raise ValueError(
                "input_teeth must be greater than zero."
            )

        if output_teeth <= 0:
            raise ValueError(
                "output_teeth must be greater than zero."
            )

        # Gear ratio
        gear_ratio = output_teeth / input_teeth

        # Ideal output torque:
        #
        # T_out = T_in * GR
        #
        # Including efficiency:
        #
        # T_out = T_in * GR * efficiency

        return (
            input_torque
            * gear_ratio
            * efficiency
        )

    # ---------------------------------------------------------
    # POWER
    # ---------------------------------------------------------

    elif operation == "power":

        # Power from torque and speed
        #
        # P = T * omega
        #
        # omega = 2*pi*n / 60
        #
        # P = T * 2*pi*n / 60

        if input_torque is not None and input_speed is not None:

            if input_torque <= 0:
                raise ValueError(
                    "input_torque must be greater than zero."
                )

            if input_speed <= 0:
                raise ValueError(
                    "input_speed must be greater than zero."
                )

            angular_velocity = (
                2 * pi * input_speed / 60
            )

            return input_torque * angular_velocity

        if (
            output_torque_value is not None
            and output_speed_value is not None
        ):

            if output_torque_value <= 0:
                raise ValueError(
                    "output_torque_value must be greater than zero."
                )

            if output_speed_value <= 0:
                raise ValueError(
                    "output_speed_value must be greater than zero."
                )

            angular_velocity = (
                2 * pi * output_speed_value / 60
            )

            return (
                output_torque_value
                * angular_velocity
            )

        raise ValueError(
            "power requires either "
            "(input_torque and input_speed) "
            "or "
            "(output_torque_value and output_speed_value)."
        )

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )