from deployment import DEFAULT_RETRIES, DEFAULT_TIMEOUT_MS, RETRIES_ENV, TIMEOUT_ENV

def load(opts, env):
    retries = opts.retries or int(env.get(RETRIES_ENV) or DEFAULT_RETRIES)
    timeout = opts.timeout_ms if opts.timeout_ms is not None else int(env.get(TIMEOUT_ENV) or DEFAULT_TIMEOUT_MS)
    return {'retries': retries, 'timeout_ms': timeout, 'driver': opts.driver}
