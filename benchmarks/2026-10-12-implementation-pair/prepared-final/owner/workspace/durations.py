def normalize(duration):
    if not duration or not duration.get("value"):
        return None
    value = float(duration["value"])
    return value * 1000 if duration.get("unit") == "s" else value / 1000
