from typing import Optional

import requests

from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class TestRailGateway:
    def __init__(self, config: EnvConfig) -> None:
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.base_url = self.config.get_env_var('TESTRAIL_BASE_URL', 'https://your-testrail-instance.testrail.com/index.php?/api/v2')
        self.headers = {
            'Authorization': 'Bearer ' + self.config.credentials['testrail_api_key'],
            'Content-Type': 'application/json',
        }

    def is_configured(self) -> bool:
        return bool(self.base_url and self.config.credentials['testrail_api_key'] and self.config.credentials['testrail_run_id']) 

    def update_result(
        self,
        run_id: str,
        case_id: str,
        status_id: int,
        comment: Optional[str] = None,
        attachment_path: Optional[str] = None,
    ) -> bool:
        if not self.is_configured():
            self.logger.info('TestRail integration is not configured; skipping result update.')
            return False

        payload = {'status_id': status_id, 'comment': comment or ''}

        try:
            response = requests.post(
                f'{self.base_url}/add_result_for_case/{run_id}/{case_id}',
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            result_id = response.json()['id']
            self.logger.info(f'Updated TestRail result: {result_id}') 

            if attachment_path:
                self._attach_file(result_id, attachment_path) 

            return True
        except Exception as exc:
            self.logger.error(f'Failed to update TestRail result: {exc}') 
            return False

    def _attach_file(self, result_id: str, file_path: str) -> None:
        try:
            with open(file_path, 'rb') as stream:
                files = {'attachment': stream}
                response = requests.post(
                    f'{self.base_url}/add_attachment_to_result/{result_id}',
                    headers={'Authorization': 'Bearer ' + self.config.credentials['testrail_api_key']},
                    files=files,
                )
                response.raise_for_status()
                self.logger.info(f'Attached file {file_path} to result {result_id}') 
        except Exception as exc:
            self.logger.error(f'Failed to attach file {file_path}: {exc}') 


TestRailClient = TestRailGateway
