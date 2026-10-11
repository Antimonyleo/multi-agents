class LocalClient:
    def send(self, timeout_seconds, retries):
        return {'client_timeout_ms': timeout_seconds * 1000, 'retries': retries}

class RemoteClient:
    def send(self, timeout_milliseconds, retries):
        return {'client_timeout_ms': timeout_milliseconds, 'retries': retries}
