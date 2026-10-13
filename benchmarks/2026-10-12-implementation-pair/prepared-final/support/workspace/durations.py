import math
from fractions import Fraction

_UNITS = {"ms": 1, "s": 1000}


def finite(value):
    """Return value if it is representable as a finite float, else raise ValueError."""
    try:
        as_float = float(value)
    except (OverflowError, ValueError, TypeError):
        raise ValueError("number is not finite") from None
    if not math.isfinite(as_float):
        raise ValueError("number is not finite")
    return value


def exact_sum(values):
    """Sum numbers exactly and round once; ints stay ints. Raises ValueError on overflow."""
    total = Fraction(0)
    all_int = True
    for value in values:
        all_int = all_int and isinstance(value, int)
        total += Fraction(value)
    finite(total)
    return int(total) if all_int else float(total)


def normalize(duration):
    if duration is None:
        return None
    if not isinstance(duration, dict) or set(duration) != {"value", "unit"}:
        raise ValueError("invalid duration")
    value, unit = duration["value"], duration["unit"]
    if not isinstance(unit, str) or unit not in _UNITS:
        raise ValueError("invalid duration unit")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid duration value")
    finite(value)
    if value < 0:
        raise ValueError("negative duration")
    return finite(value * _UNITS[unit])
