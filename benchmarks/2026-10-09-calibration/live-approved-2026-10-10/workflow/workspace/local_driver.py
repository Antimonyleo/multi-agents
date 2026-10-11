from clients import LocalClient

def dispatch(plan):
    timeout_seconds = plan['timeout_ms'] / 1000
    return LocalClient().send(timeout_seconds, plan['retries'])
