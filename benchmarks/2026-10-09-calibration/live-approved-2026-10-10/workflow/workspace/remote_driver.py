from clients import RemoteClient

def dispatch(plan):
    timeout_milliseconds = plan['timeout_ms'] / 1000
    return RemoteClient().send(timeout_milliseconds, plan['retries'])
