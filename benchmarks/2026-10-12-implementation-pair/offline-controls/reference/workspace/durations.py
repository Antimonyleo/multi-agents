import math

def normalize(duration):
    if duration is None:
        return None
    if not isinstance(duration, dict) or set(duration) != {"value", "unit"}:
        raise ValueError("duration")
    value, unit = duration["value"], duration["unit"]
    if type(value) not in (int, float) or unit not in ("ms", "s") or type(unit) is not str:
        raise ValueError("duration")
    try:
        value = float(value)
        amount = value if unit == "ms" else value * 1000
    except (OverflowError, ValueError):
        raise ValueError("duration")
    if not math.isfinite(amount) or amount < 0:
        raise ValueError("duration")
    return amount
