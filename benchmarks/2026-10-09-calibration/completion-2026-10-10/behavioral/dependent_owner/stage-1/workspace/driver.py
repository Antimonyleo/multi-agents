def dispatch(plan):
    return {"retries": plan["retries"], "seconds": plan["deadline_ms"] / 1000000}
