import json
import sys
from attempts import summarize

def generate(payload):
    rows = summarize(payload["attempts"])
    total = round(sum(row["known_duration_ms"] for row in rows), 2)
    return {"jobs": rows, "totals": {"jobs": len(rows),
        "successful_jobs": sum(row["state"] == "success" for row in rows),
        "failed_jobs": sum(row["state"] == "failed" for row in rows),
        "stopped_jobs": sum(row["state"] == "stopped" for row in rows),
        "known_duration_ms": total, "duration_ms": total, "unknown_attempts": 0}}

if __name__ == "__main__":
    print(json.dumps(generate(json.load(sys.stdin))))
