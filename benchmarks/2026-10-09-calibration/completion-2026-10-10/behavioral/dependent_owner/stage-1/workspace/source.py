def resolve(opts, env):
    return {"retries": opts.get("retries") or int(env.get("RETRIES", 2)), "deadline_ms": opts.get("deadline_ms", 125)}
