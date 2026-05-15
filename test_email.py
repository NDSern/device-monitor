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
    recipient = config.RECIPIENT_EMAILS[0]

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

    try:
        print("Connecting to smtp.office365.com:587...")
        if True:
            server = smtplib.SMTP("smtp.office365.com", 587)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL("smtp.office365.com", 587)

        print(f"Logging in as {config.SENDER_EMAIL}...")
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)

        print(f"Sending test email to {recipient}...")
        server.sendmail(config.SENDER_EMAIL, [recipient], msg.as_string())
        server.quit()

        print("Test email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP authentication failed: {e}")
        print("Check your SENDER_EMAIL and SENDER_PASSWORD in config.py")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    send_test_email()
