from __future__ import annotations

import os
import smtplib
import zipfile
from dataclasses import dataclass
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional, Sequence
from xml.etree import ElementTree


def _str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class EmailConfig:
    enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str
    email_to: Sequence[str]
    use_tls: bool
    subject_prefix: str


def load_email_config_from_env() -> EmailConfig:
    enabled = _str_to_bool(os.getenv("EMAIL_ENABLED"), default=False)
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    email_from = os.getenv("EMAIL_FROM", "").strip() or smtp_username
    email_to_raw = os.getenv("EMAIL_TO", "").strip()
    email_to = [x.strip() for x in email_to_raw.split(",") if x.strip()]
    use_tls = _str_to_bool(os.getenv("EMAIL_USE_TLS"), default=True)
    subject_prefix = os.getenv("EMAIL_SUBJECT_PREFIX", "Playwright Tests").strip()

    return EmailConfig(
        enabled=enabled,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        email_from=email_from,
        email_to=email_to,
        use_tls=use_tls,
        subject_prefix=subject_prefix,
    )


def _parse_junit_summary(junit_xml_path: Path) -> dict:
    """
    Extracts summary and up to a few failure details from `reports/junit-report.xml`.
    """
    if not junit_xml_path.exists():
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "failure_details": []}

    tree = ElementTree.parse(junit_xml_path)
    root = tree.getroot()

    # First testsuite is what this project uses.
    suite = next(iter(root.findall(".//testsuite")), None)
    if suite is None:
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "failure_details": []}

    tests = int(suite.attrib.get("tests", "0"))
    failures = int(suite.attrib.get("failures", "0"))
    errors = int(suite.attrib.get("errors", "0"))
    skipped = int(suite.attrib.get("skipped", "0"))

    failure_details: list[str] = []
    for tc in suite.findall(".//testcase"):
        failure_el = tc.find("failure")
        if failure_el is not None and failure_el.text:
            class_name = tc.attrib.get("classname", "")
            name = tc.attrib.get("name", "")
            failure_details.append(f"{class_name}::{name}\n{failure_el.text.strip()}")
        if len(failure_details) >= 5:
            break

    return {
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "failure_details": failure_details,
    }


def _zip_report_artifacts(
    zip_path: Path,
    report_html_path: Path,
    junit_xml_path: Path,
    logs_dir_path: Path,
) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if report_html_path.exists():
            zf.write(report_html_path, arcname=report_html_path.name)
        if junit_xml_path.exists():
            zf.write(junit_xml_path, arcname=junit_xml_path.name)

        if logs_dir_path.exists() and logs_dir_path.is_dir():
            # Store logs with relative paths under `logs/`
            for p in logs_dir_path.rglob("*"):
                if p.is_file():
                    zf.write(p, arcname=str(Path("logs") / p.relative_to(logs_dir_path)))


def _send_email(
    *,
    cfg: EmailConfig,
    subject: str,
    body_text: str,
    attachment_zip_path: Optional[Path] = None,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = cfg.email_from
    msg["To"] = ", ".join(cfg.email_to)
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    if attachment_zip_path and attachment_zip_path.exists():
        with attachment_zip_path.open("rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_zip_path.name)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment_zip_path.name}"',
        )
        msg.attach(part)

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as smtp:
        if cfg.use_tls:
            smtp.starttls()
        if cfg.smtp_username:
            smtp.login(cfg.smtp_username, cfg.smtp_password)
        smtp.sendmail(cfg.email_from, list(cfg.email_to), msg.as_string())


def try_send_email_report(*, env_name: str = "", dry_run: bool = False) -> None:
    cfg = load_email_config_from_env()
    if not cfg.enabled:
        return

    required = [cfg.smtp_host, cfg.smtp_username, cfg.smtp_password, cfg.email_from]
    if any(not x for x in required) or not cfg.email_to:
        # Don’t throw hard here; treat as “misconfigured email”.
        return

    reports_dir = Path("reports")
    report_html_path = reports_dir / "report.html"
    junit_xml_path = reports_dir / "junit-report.xml"
    logs_dir_path = reports_dir / "logs"

    summary = _parse_junit_summary(junit_xml_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = reports_dir / f"email_artifacts_{ts}.zip"

    if not dry_run:
        _zip_report_artifacts(
            zip_path=zip_path,
            report_html_path=report_html_path,
            junit_xml_path=junit_xml_path,
            logs_dir_path=logs_dir_path,
        )

    failed_count = int(summary.get("failures", 0)) + int(summary.get("errors", 0))
    subject = f"{cfg.subject_prefix} - {env_name or 'env'} - {summary['tests']} tests - {failed_count} failures"

    failure_preview = ""
    details = summary.get("failure_details") or []
    if details:
        failure_preview = "\n\nFailure preview:\n" + "\n---\n".join(details[:3])

    body_text = (
        f"Playwright test run completed.\n"
        f"Environment: {env_name or 'N/A'}\n"
        f"Total: {summary['tests']}\n"
        f"Passed: {summary['tests'] - failed_count - int(summary.get('skipped', 0))}\n"
        f"Failures: {failed_count}\n"
        f"Skipped: {summary.get('skipped', 0)}\n"
        f"\nSee attached artifacts (includes reports/report.html and reports/logs/)."
        f"{failure_preview}"
    )

    if dry_run:
        return

    _send_email(
        cfg=cfg,
        subject=subject,
        body_text=body_text,
        attachment_zip_path=zip_path,
    )

