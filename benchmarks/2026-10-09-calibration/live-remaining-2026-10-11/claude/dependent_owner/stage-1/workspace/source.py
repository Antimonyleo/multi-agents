def resolve(opts, env):
    retries = opts["retries"] if "retries" in opts else int(env.get("RETRIES", 2))
    return {"retries": retries, "deadline_ms": opts.get("deadline_ms", 125)}
