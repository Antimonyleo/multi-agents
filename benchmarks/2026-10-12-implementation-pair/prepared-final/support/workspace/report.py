import json
import sys
from attempts import summarize
from durations import exact_sum

INVALID = {"error": "invalid_input"}


def generate(payload):
    try:
        if not isinstance(payload, dict) or "attempts" not in payload:
            raise ValueError("invalid payload")
        rows = sorted(summarize(payload["attempts"]), key=lambda row: row["job"])
        known = exact_sum(row["known_duration_ms"] for row in rows)
    except ValueError:
        return dict(INVALID)
    unknown = sum(row["unknown_attempts"] for row in rows)
    return {"jobs": rows, "totals": {"jobs": len(rows),
        "successful_jobs": sum(1 for row in rows if row["state"] == "success"),
        "failed_jobs": sum(1 for row in rows if row["state"] == "failed"),
        "stopped_jobs": sum(1 for row in rows if row["state"] == "stopped"),
        "known_duration_ms": known, "duration_ms": known if unknown == 0 else None,
        "unknown_attempts": unknown}}


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read())
    except (ValueError, RecursionError):
        result = dict(INVALID)
    else:
        result = generate(payload)
    sys.stdout.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
