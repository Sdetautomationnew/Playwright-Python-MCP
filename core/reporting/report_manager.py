from typing import Dict

from core.reporting.allure_adapter import AllureAdapter
from core.reporting.html_report_adapter import HtmlReportAdapter


class ReportManager:
    def __init__(self) -> None:
        self.html = HtmlReportAdapter()
        self.allure = AllureAdapter()

    def as_dict(self) -> Dict[str, str]:
        return {'html': self.html.output_path, 'allure': self.allure.output_path}
