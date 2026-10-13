from durations import normalize

def summarize(records):
    groups = {}
    for record in records:
        job = record["job"]
        row = groups.setdefault(job, {"job": job, "attempts": 0, "last_attempt": 0,
            "state": "failed", "duration_ms": 0, "known_duration_ms": 0, "unknown_attempts": 0})
        row["attempts"] += 1
        row["last_attempt"] = record["attempt"]
        if record["status"] == "success":
            row["state"] = "success"
        amount = normalize(record.get("duration"))
        row["known_duration_ms"] += amount or 0
        row["duration_ms"] = row["known_duration_ms"]
    return list(groups.values())
