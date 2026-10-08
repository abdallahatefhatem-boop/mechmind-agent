from typing import Literal
from langchain_core.tools import tool


@tool
def spring_design(
    operation: Literal[
        "spring_force",
        "spring_deflection",
        "spring_rate",
    ],
    force: float | None = None,
    deflection: float | None = None,
    spring_rate_value: float | None = None,
) -> float:
    """
    Calculate spring force, deflection, or spring rate
    using Hooke's law for a linear spring.

    Hooke's law:

        F = k * x

    where:

        F = spring force [N]
        k = spring stiffness/rate [N/m]
        x = spring deflection [m]

    Supported operations:

    1. spring_force
       Calculate force from spring rate and deflection.

           F = k * x

       Requires:
           spring_rate_value
           deflection

    2. spring_deflection
       Calculate deflection from force and spring rate.

           x = F / k

       Requires:
           force
           spring_rate_value

    3. spring_rate
       Calculate spring stiffness from force and deflection.

           k = F / x

       Requires:
           force
           deflection

    Units:
        force -> N
        deflection -> m
        spring_rate -> N/m

    Important:
        This tool assumes a linear spring operating within its
        elastic range. It does not calculate coil geometry,
        stress, fatigue life, or buckling.
    """

    # ---------------------------------------------------------
    # SPRING FORCE
    # ---------------------------------------------------------

    if operation == "spring_force":

        if spring_rate_value is None:
            raise ValueError(
                "spring_rate_value is required for spring_force."
            )

        if deflection is None:
            raise ValueError(
                "deflection is required for spring_force."
            )

        if spring_rate_value <= 0:
            raise ValueError(
                "spring_rate_value must be greater than zero."
            )

        if deflection < 0:
            raise ValueError(
                "deflection cannot be negative."
            )

        # Hooke's law:
        #
        # F = k*x

        return spring_rate_value * deflection

    # ---------------------------------------------------------
    # SPRING DEFLECTION
    # ---------------------------------------------------------

    elif operation == "spring_deflection":

        if force is None:
            raise ValueError(
                "force is required for spring_deflection."
            )

        if spring_rate_value is None:
            raise ValueError(
                "spring_rate_value is required for spring_deflection."
            )

        if force < 0:
            raise ValueError(
                "force cannot be negative."
            )

        if spring_rate_value <= 0:
            raise ValueError(
                "spring_rate_value must be greater than zero."
            )

        # x = F/k

        return force / spring_rate_value

    # ---------------------------------------------------------
    # SPRING RATE
    # ---------------------------------------------------------

    elif operation == "spring_rate":

        if force is None:
            raise ValueError(
                "force is required for spring_rate."
            )

        if deflection is None:
            raise ValueError(
                "deflection is required for spring_rate."
            )

        if force < 0:
            raise ValueError(
                "force cannot be negative."
            )

        if deflection <= 0:
            raise ValueError(
                "deflection must be greater than zero."
            )

        # k = F/x

        return force / deflection

    # ---------------------------------------------------------
    # INVALID OPERATION
    # ---------------------------------------------------------

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )