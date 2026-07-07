from typing import Optional

GRAVITY_SEVERITY_MAP = {
    "Heinous": 5.0,
    "Non-Heinous": 2.0,
    "Special": 3.0,
}

DEFAULT_SEVERITY = 2.0

def resolve_gravity_severity(gravity_name: Optional[str]) -> float:
    """
    Translates GravityOffence names into severity scores.
    """
    if not gravity_name:
        return DEFAULT_SEVERITY
    return GRAVITY_SEVERITY_MAP.get(gravity_name, DEFAULT_SEVERITY)
