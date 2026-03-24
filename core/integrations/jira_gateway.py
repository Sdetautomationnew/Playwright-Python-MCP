from typing import List, Optional

import requests

from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class JiraGateway:
    def __init__(self, config: EnvConfig) -> None:
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.base_url = self.config.get_env_var('JIRA_BASE_URL', 'https://your-jira-instance.atlassian.net/rest/api/2')
        self.headers = {
            'Authorization': 'Bearer ' + self.config.credentials['jira_api_token'],
            'Content-Type': 'application/json',
        }

    def is_configured(self) -> bool:
        return bool(self.base_url and self.config.credentials['jira_api_token'] and self.config.credentials['jira_project_key']) 

    def create_issue(
        self,
        summary: str,
        description: str,
        attachments: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        env_metadata: Optional[dict] = None,
    ) -> Optional[str]:
        if not self.is_configured():
            self.logger.info('Jira integration is not configured; skipping issue creation.')
            return None

        payload = {
            'fields': {
                'project': {'key': self.config.credentials['jira_project_key']},
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Bug'},
                'labels': labels or [],
            }
        }

        if env_metadata:
            payload['fields']['description'] += '\n\nEnvironment: ' + str(env_metadata) 

        try:
            response = requests.post(f'{self.base_url}/issue', json=payload, headers=self.headers) 
            response.raise_for_status()
            issue_key = response.json()['key']
            self.logger.info(f'Created Jira issue: {issue_key}') 

            if attachments:
                for attachment in attachments:
                    self._attach_file(issue_key, attachment) 

            return issue_key
        except Exception as exc:
            self.logger.error(f'Failed to create Jira issue: {exc}') 
            return None

    def _attach_file(self, issue_key: str, file_path: str) -> None:
        try:
            with open(file_path, 'rb') as stream:
                files = {'file': stream}
                response = requests.post(
                    f'{self.base_url}/issue/{issue_key}/attachments',
                    headers={
                        'Authorization': 'Bearer ' + self.config.credentials['jira_api_token'],
                        'X-Atlassian-Token': 'no-check',
                    },
                    files=files,
                )
                response.raise_for_status()
                self.logger.info(f'Attached file {file_path} to issue {issue_key}') 
        except Exception as exc:
            self.logger.error(f'Failed to attach file {file_path}: {exc}') 


JiraClient = JiraGateway
