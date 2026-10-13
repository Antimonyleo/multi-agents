from durations import exact_sum, normalize

_STATUSES = ("success", "failed", "stopped")


def _validate(record):
    if not isinstance(record, dict) or not {"job", "attempt", "status"} <= set(record):
        raise ValueError("invalid record")
    job, attempt, status = record["job"], record["attempt"], record["status"]
    if not isinstance(job, str) or not job.strip():
        raise ValueError("invalid job")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise ValueError("invalid attempt")
    if not isinstance(status, str) or status not in _STATUSES:
        raise ValueError("invalid status")
    return job, attempt, status, normalize(record.get("duration"))


def summarize(records):
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    groups = {}
    for record in records:
        job, attempt, status, amount = _validate(record)
        attempts = groups.setdefault(job, {})
        if attempt in attempts:
            raise ValueError("duplicate attempt")
        attempts[attempt] = (status, amount)
    rows = []
    for job, attempts in groups.items():
        last_attempt = max(attempts)
        known = [amount for _, amount in attempts.values() if amount is not None]
        unknown = len(attempts) - len(known)
        known_ms = exact_sum(known)
        rows.append({"job": job, "attempts": len(attempts), "last_attempt": last_attempt,
            "state": attempts[last_attempt][0], "duration_ms": known_ms if unknown == 0 else None,
            "known_duration_ms": known_ms, "unknown_attempts": unknown})
    return rows
