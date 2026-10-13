import json
import math
import sys
from attempts import summarize

def generate(payload):
    try:
        if not isinstance(payload, dict) or "attempts" not in payload:
            raise ValueError("payload")
        rows = summarize(payload["attempts"])
        known = sum(row["known_duration_ms"] for row in rows)
        if not math.isfinite(known):
            raise ValueError("overflow")
        unknown = sum(row["unknown_attempts"] for row in rows)
        return {"jobs": rows, "totals": {"jobs": len(rows),
            "successful_jobs": sum(row["state"] == "success" for row in rows),
            "failed_jobs": sum(row["state"] == "failed" for row in rows),
            "stopped_jobs": sum(row["state"] == "stopped" for row in rows),
            "known_duration_ms": known, "duration_ms": None if unknown else known,
            "unknown_attempts": unknown}}
    except ValueError:
        return {"error": "invalid_input"}

if __name__ == "__main__":
    try:
        result = generate(json.load(sys.stdin))
    except ValueError:
        result = {"error": "invalid_input"}
    print(json.dumps(result, allow_nan=False))
