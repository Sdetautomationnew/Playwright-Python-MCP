from core.reporting.telemetry_client import get_logger


class SlackNotifier:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    def send(self, message: str) -> None:
        self.logger.info(f'Slack notification: {message}')
