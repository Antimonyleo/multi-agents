import math
from durations import normalize

def summarize(records):
    if not isinstance(records, list):
        raise ValueError("records")
    groups, seen = {}, set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("record")
        job, attempt, status = record.get("job"), record.get("attempt"), record.get("status")
        if not isinstance(job, str) or not job.strip() or type(attempt) is not int or attempt < 1 or status not in ("success", "failed", "stopped"):
            raise ValueError("record")
        identity = job, attempt
        if identity in seen:
            raise ValueError("duplicate")
        seen.add(identity)
        row = groups.setdefault(job, {"job": job, "attempts": 0, "last_attempt": 0,
            "state": "failed", "duration_ms": 0, "known_duration_ms": 0, "unknown_attempts": 0})
        row["attempts"] += 1
        if attempt > row["last_attempt"]:
            row["last_attempt"], row["state"] = attempt, status
        amount = normalize(record.get("duration"))
        if amount is None:
            row["unknown_attempts"] += 1
        else:
            row["known_duration_ms"] += amount
            try:
                if not math.isfinite(row["known_duration_ms"]):
                    raise ValueError("overflow")
            except OverflowError:
                raise ValueError("overflow")
    for row in groups.values():
        row["duration_ms"] = None if row["unknown_attempts"] else row["known_duration_ms"]
    return sorted(groups.values(), key=lambda row: row["job"])
