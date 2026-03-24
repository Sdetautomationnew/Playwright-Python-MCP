class RetryOrchestrator:
    def __init__(self, retries=3):
        self.retries = retries

    def run(self, action):
        last_error = None
        for _ in range(self.retries + 1):
            try:
                return action()
            except Exception as exc:
                last_error = exc
        raise last_error
