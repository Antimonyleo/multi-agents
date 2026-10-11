def validate(config):
    if not 0 <= config['retries'] <= 5:
        raise ValueError('retries_range')
    if not 10 <= config['timeout_ms'] <= 500:
        raise ValueError('timeout_range')
    return config
