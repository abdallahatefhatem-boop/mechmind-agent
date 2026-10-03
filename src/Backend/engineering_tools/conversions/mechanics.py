from langchain_core.tools import tool


# =========================
# Unit Definitions
# =========================

MASS_UNITS = {
    "kg": 1.0,
    "g": 1e-3,
    "mg": 1e-6,
    "lb": 0.45359237,
    "oz": 0.028349523125,
}


ACCELERATION_UNITS = {
    "m/s2": 1.0,
    "cm/s2": 0.01,
    "ft/s2": 0.3048,
    "g": 9.80665,
}


FORCE_UNITS = {
    "N": 1.0,
    "kN": 1e3,
    "MN": 1e6,
    "dyn": 1e-5,
    "lbf": 4.4482216152605,
}


TORQUE_UNITS = {
    "N*m": 1.0,
    "kN*m": 1e3,
    "N*cm": 0.01,
    "N*mm": 0.001,
    "lbf*ft": 1.3558179483,
    "lbf*in": 0.112984829,
}


WORK_UNITS = {
    "J": 1.0,
    "kJ": 1e3,
    "MJ": 1e6,
    "Wh": 3600.0,
    "kWh": 3.6e6,
    "ft*lbf": 1.3558179483,
}


ENERGY_UNITS = {
    "J": 1.0,
    "kJ": 1e3,
    "MJ": 1e6,
    "Wh": 3600.0,
    "kWh": 3.6e6,
    "cal": 4.184,
    "kcal": 4184.0,
    "eV": 1.602176634e-19,
}


POWER_UNITS = {
    "W": 1.0,
    "kW": 1e3,
    "MW": 1e6,
    "hp": 745.699872,
}


STRESS_UNITS = {
    "Pa": 1.0,
    "kPa": 1e3,
    "MPa": 1e6,
    "GPa": 1e9,
    "psi": 6894.757293,
    "ksi": 6.894757293e6,
}


STRAIN_UNITS = {
    "strain": 1.0,
    "%": 0.01,
    "microstrain": 1e-6,
}


# =========================
# Generic Conversion
# =========================

def _convert(
    value: float,
    from_unit: str,
    to_unit: str,
    units: dict,
) -> float:

    if from_unit not in units:
        raise ValueError(
            f"Unsupported source unit: {from_unit}"
        )

    if to_unit not in units:
        raise ValueError(
            f"Unsupported target unit: {to_unit}"
        )

    value_in_si = value * units[from_unit]

    return value_in_si / units[to_unit]


# =========================
# Conversion Tools
# =========================

@tool
def convert_force(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert force between N, kN, MN, dyn and lbf.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        FORCE_UNITS,
    )


@tool
def convert_mass(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert mass between kg, g, mg, lb and oz.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        MASS_UNITS,
    )


@tool
def convert_acceleration(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert acceleration between m/s2, cm/s2, ft/s2 and g.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        ACCELERATION_UNITS,
    )


@tool
def convert_torque(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert torque between N*m, kN*m, N*cm,
    N*mm, lbf*ft and lbf*in.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        TORQUE_UNITS,
    )


@tool
def convert_work(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert work between J, kJ, MJ, Wh, kWh and ft*lbf.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        WORK_UNITS,
    )


@tool
def convert_energy(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert energy between J, kJ, MJ, Wh, kWh,
    cal, kcal and eV.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        ENERGY_UNITS,
    )


@tool
def convert_power(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert power between W, kW, MW and hp.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        POWER_UNITS,
    )


@tool
def convert_stress(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert stress between Pa, kPa, MPa, GPa,
    psi and ksi.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        STRESS_UNITS,
    )


@tool
def convert_strain(
    value: float,
    from_unit: str,
    to_unit: str,
) -> float:
    """
    Convert strain between strain, %, and microstrain.
    """
    return _convert(
        value,
        from_unit,
        to_unit,
        STRAIN_UNITS,
    )