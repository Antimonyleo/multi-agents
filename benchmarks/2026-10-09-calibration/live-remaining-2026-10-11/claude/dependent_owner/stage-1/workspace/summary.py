def mean(readings):
    readings = list(readings)
    if not readings:
        raise ValueError("empty readings")
    return sum(readings) / len(readings)
