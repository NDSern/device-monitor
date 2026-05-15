"""
Test Email Script
Sends a single test email to verify SMTP configuration.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import socket

import config


def send_test_email():
    """Send a test email to verify SMTP configuration."""
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recipients = config.get_recipient_emails()
    if not recipients:
        print("No recipient emails configured.")
        return
    recipient = recipients[0]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[TEST] Resource Tracker - {hostname}"
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = recipient

    body = f"""
Resource Tracker - Test Email

Hostname: {hostname}
Timestamp: {timestamp}

This is a test email to verify the SMTP configuration.
If you received this, the email alert system is working correctly.
"""

    msg.attach(MIMEText(body, "plain"))

    server = None
    try:
        print(f"Connecting to {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        if config.EMAIL_USE_TLS:
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)

        print(f"Logging in as {config.SENDER_EMAIL}...")
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)

        print(f"Sending test email to {recipient}...")
        server.sendmail(config.SENDER_EMAIL, [recipient], msg.as_string())

        print("Test email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP authentication failed: {e}")
        print("Check your SENDER_EMAIL and SENDER_PASSWORD in config.py")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if server is not None:
            try:
                server.quit()
            except smtplib.SMTPException:
                pass


if __name__ == "__main__":
    send_test_email()
