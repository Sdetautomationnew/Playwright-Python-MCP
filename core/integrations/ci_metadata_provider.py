import os


class CIMetadataProvider:
    def collect(self):
        keys = ('GITHUB_ACTIONS', 'GITHUB_RUN_ID', 'BUILD_NUMBER', 'JOB_NAME')
        return {key: os.getenv(key, '') for key in keys if os.getenv(key)} 
