from config.defaults import DEADLINE_MS, RETRY_ENV
def resolve(opts, env):
    retries = opts.get("retries")
    if retries is None:
        retries = int(env.get(RETRY_ENV, 2))
    return {"deadline_ms": DEADLINE_MS, "retries": retries}
