"""
Email Alert Module
Sends email warnings when system resources exceed defined thresholds.
"""

import smtplib
import logging
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import config

logger = logging.getLogger(__name__)

TRANSIENT_EMAIL_ERRORS = (
    socket.gaierror,
    TimeoutError,
    OSError,
    smtplib.SMTPConnectError,
    smtplib.SMTPServerDisconnected,
)


class EmailAlert:
    """Handles sending email alerts when resource usage exceeds thresholds."""

    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.use_tls = config.EMAIL_USE_TLS
        self.sender_email = config.SENDER_EMAIL
        self.sender_password = config.SENDER_PASSWORD

    def _send_message(self, msg: MIMEMultipart, success_message: str) -> bool:
        if not config.EMAIL_ENABLED:
            logger.info("Email alerts are disabled. Skipping.")
            return False

        recipients = config.get_recipient_emails()
        if not recipients:
            logger.warning("No recipient emails configured. Skipping email send.")
            return False

        recipient_header = ", ".join(recipients)
        if "To" in msg:
            msg.replace_header("To", recipient_header)
        else:
            msg["To"] = recipient_header

        retry_delays = getattr(config, "EMAIL_SEND_RETRY_DELAYS_SECONDS", [])
        total_attempts = len(retry_delays) + 1

        for attempt in range(1, total_attempts + 1):
            server = None
            try:
                logger.info(
                    f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port} "
                    f"(attempt {attempt}/{total_attempts})"
                )
                if self.use_tls:
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)

                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())

                logger.info(success_message)
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed: {e}")
                return False
            except TRANSIENT_EMAIL_ERRORS as e:
                if attempt >= total_attempts:
                    logger.error(f"Failed to send email alert after {attempt} attempts: {e}")
                    return False
                delay = retry_delays[attempt - 1]
                logger.warning(
                    f"Email send attempt {attempt}/{total_attempts} failed: {e}. "
                    f"Retrying in {delay}s."
                )
                time.sleep(delay)
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error occurred: {e}")
                return False
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
                return False
            finally:
                if server is not None:
                    try:
                        server.quit()
                    except smtplib.SMTPException:
                        logger.debug("Failed to close SMTP connection cleanly")

        return False

    def _create_alert_message(self, resource_name: str, usage: float, threshold: float,
                              hostname: str, timestamp: str,
                              cpu_usage: float = 0, ram_usage: float = 0,
                              npu_usage: list = None) -> MIMEMultipart:
        """
        Create an email message for resource alert.

        Args:
            resource_name: Name of the resource (CPU, RAM, or NPU Core)
            usage: Current usage percentage
            threshold: Threshold that was exceeded
            hostname: System hostname
            timestamp: Time of the alert
            cpu_usage: Current CPU usage for context
            ram_usage: Current RAM usage for context
            npu_usage: List of NPU core usage percentages

        Returns:
            MIMEMultipart: Email message object
        """
        if npu_usage is None:
            npu_usage = [0.0, 0.0, 0.0]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = config.EMAIL_SUBJECT_ALERT.format(hostname=hostname)
        msg["From"] = self.sender_email

        body = config.EMAIL_BODY_TEMPLATE.format(
            resource_name=resource_name,
            hostname=hostname,
            timestamp=timestamp,
            usage=usage,
            threshold=threshold,
            cpu_usage=cpu_usage,
            ram_usage=ram_usage,
            npu_core_0=npu_usage[0],
            npu_core_1=npu_usage[1],
            npu_core_2=npu_usage[2],
        )

        msg.attach(MIMEText(body, "html", "utf-8"))
        return msg

    def send_alert(self, resource_name: str, usage: float, threshold: float,
                   hostname: str, timestamp: str,
                   cpu_usage: float = 0, ram_usage: float = 0,
                   npu_usage: list = None) -> bool:
        """
        Send an alert email to all configured recipients.

        Args:
            resource_name: Name of the resource (CPU, RAM, or NPU Core)
            usage: Current usage percentage
            threshold: Threshold that was exceeded
            hostname: System hostname
            timestamp: Time of the alert
            cpu_usage: Current CPU usage for context
            ram_usage: Current RAM usage for context
            npu_usage: List of NPU core usage percentages

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        msg = self._create_alert_message(
            resource_name, usage, threshold, hostname, timestamp,
            cpu_usage, ram_usage, npu_usage
        )
        return self._send_message(
            msg,
            f"Alert email sent successfully for {resource_name} ({usage:.1f}%)",
        )

    def send_status_email(self, subject: str, body: str, hostname: str, timestamp: str) -> bool:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg.attach(MIMEText(body, "html", "utf-8"))
        return self._send_message(msg, f"Status email sent successfully at {timestamp} from {hostname}")

class AlertManager:
    """Manages resource alerts and prevents duplicate notifications."""

    def __init__(self):
        self.email_alert = EmailAlert()
        self.alert_cooldowns = {}  # Track last alert time per resource
        self.camera_status = {}

    def check_and_alert(self, resource_name: str, usage: float, threshold: float,
                        hostname: str, timestamp: str,
                        cpu_usage: float = 0, ram_usage: float = 0,
                        npu_usage: list = None) -> bool:
        """
        Check if usage exceeds threshold and send alert if needed.

        Args:
            resource_name: Name of the resource (CPU, RAM, or NPU Core)
            usage: Current usage percentage
            threshold: Threshold percentage
            hostname: System hostname
            timestamp: Time of check
            cpu_usage: Current CPU usage for context
            ram_usage: Current RAM usage for context
            npu_usage: List of NPU core usage percentages

        Returns:
            bool: True if alert was sent, False otherwise
        """
        if usage >= threshold:
            now = time.monotonic()
            last_alert_time = self.alert_cooldowns.get(resource_name)
            if last_alert_time is not None and now - last_alert_time < config.ALERT_COOLDOWN_SECONDS:
                logger.warning(
                    f"ALERT SUPPRESSED: {resource_name} usage at {usage:.1f}% "
                    f"(threshold: {threshold}%, cooldown active)"
                )
                return False

            logger.warning(
                f"ALERT: {resource_name} usage at {usage:.1f}% "
                f"(threshold: {threshold}%)"
            )
            sent = self.email_alert.send_alert(
                resource_name, usage, threshold, hostname, timestamp,
                cpu_usage, ram_usage, npu_usage
            )
            if sent:
                self.alert_cooldowns[resource_name] = now
            return sent
        else:
            self.alert_cooldowns.pop(resource_name, None)
            logger.debug(f"{resource_name} usage normal: {usage:.1f}%")
            return False

    @staticmethod
    def _camera_row(ip: str, name: str, is_online: bool, highlight: bool = False) -> str:
        status = "Đang kết nối" if is_online else "Mất kết nối"
        color = "#15803d" if is_online else "#b91c1c"
        bg = "background:#ecfdf5;" if highlight and is_online else "background:#fef2f2;" if highlight else ""
        return (
            f'<tr style="{bg}"><td style="border:1px solid #ddd;padding:8px;color:{color};font-weight:bold;">{status}</td>'
            f'<td style="border:1px solid #ddd;padding:8px;">{name}</td>'
            f'<td style="border:1px solid #ddd;padding:8px;">{ip}</td></tr>'
        )

    def _format_all_camera_rows(self, changed: list[tuple[str, str]] | None = None) -> str:
        cameras = config.get_cameras()
        changed_ips = {ip for ip, _ in (changed or [])}
        return "".join(
            self._camera_row(ip, name, self.camera_status.get(ip, True), ip in changed_ips)
            for ip, name in cameras.items()
        )

    def send_camera_down_alert(self, cameras: list[tuple[str, str]], hostname: str, timestamp: str) -> bool:
        body = config.CAMERA_DOWN_BODY_TEMPLATE.format(
            hostname=hostname,
            timestamp=timestamp,
            camera_rows=self._format_all_camera_rows(cameras),
        )
        return self.email_alert.send_status_email(config.CAMERA_DOWN_SUBJECT, body, hostname, timestamp)

    def send_camera_up_alert(self, cameras: list[tuple[str, str]], hostname: str, timestamp: str) -> bool:
        body = config.CAMERA_UP_BODY_TEMPLATE.format(
            hostname=hostname,
            timestamp=timestamp,
            camera_rows=self._format_all_camera_rows(cameras),
        )
        return self.email_alert.send_status_email(config.CAMERA_UP_SUBJECT, body, hostname, timestamp)

    def check_camera_transitions(self, unreachable: list[tuple[str, str]], hostname: str, timestamp: str) -> None:
        cameras = config.get_cameras()
        stale_ips = set(self.camera_status) - set(cameras)
        for ip in stale_ips:
            del self.camera_status[ip]

        unreachable_ips = {ip for ip, _ in unreachable}
        newly_down = []
        back_up = []

        for ip, name in cameras.items():
            is_online = ip not in unreachable_ips
            was_online = self.camera_status.get(ip)

            if was_online is None:
                state = "online" if is_online else "offline"
                logger.info(f"Initial camera state: {name} ({ip}) is {state}")
            elif was_online and not is_online:
                newly_down.append((ip, name))
            elif not was_online and is_online:
                back_up.append((ip, name))

            self.camera_status[ip] = is_online

        if newly_down:
            logger.warning(f"Camera(s) offline: {newly_down}")
            self.send_camera_down_alert(newly_down, hostname, timestamp)

        if back_up:
            logger.info(f"Camera(s) back online: {back_up}")
            self.send_camera_up_alert(back_up, hostname, timestamp)

    def send_boot_alert(self, hostname: str, timestamp: str, last_active_time: str) -> bool:
        body = config.BOOT_BODY_TEMPLATE.format(
            hostname=hostname,
            timestamp=timestamp,
            last_active_time=last_active_time,
        )
        return self.email_alert.send_status_email(config.BOOT_SUBJECT, body, hostname, timestamp)


def build_status_body(alert_manager: AlertManager, hostname: str, timestamp: str) -> str:
    return config.STATUS_BODY_TEMPLATE.format(
        hostname=hostname,
        timestamp=timestamp,
        camera_rows=alert_manager._format_all_camera_rows(),
    )
