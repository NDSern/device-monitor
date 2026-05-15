# Resource Tracker

A Python application that monitors CPU and RAM usage on your machine and sends email warnings when any resource reaches 90% usage.

## Features

- **Real-time Monitoring**: Tracks CPU and RAM usage
- **Configurable Thresholds**: Default 90% alert threshold for both CPU and RAM
- **Email Alerts**: Sends SMTP email notifications when thresholds are exceeded
- **Scheduled Checks**: Runs every 5 minutes (configurable)
- **Logging**: All checks and alerts are logged to a file

## Project Structure

```
resource-tracker/
├── main.py           # Main application entry point
├── monitor.py        # CPU and RAM monitoring module
├── email_alert.py    # Email alert backbone
├── config.py         # Configuration settings
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── resource_tracker.log  # Auto-generated log file
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure email settings in `config.py`:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"  # Use Gmail app password
RECIPIENT_EMAILS = ["admin@example.com"]
```

### Gmail Setup (if using Gmail)

1. Enable 2-Step Verification on your Google Account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in `config.py`

## Usage

Run the resource tracker:

```bash
python main.py
```

The application will:
- Start monitoring CPU and RAM every 5 minutes
- Log all checks to `resource_tracker.log`
- Send email alerts when CPU or RAM exceeds 90%

**Stop the tracker**: Press `Ctrl+C`

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `MONITORING_INTERVAL_SECONDS` | 300 | Seconds between checks |
| `CPU_THRESHOLD` | 90 | CPU alert threshold (%) |
| `RAM_THRESHOLD` | 90 | RAM alert threshold (%) |
| `EMAIL_ENABLED` | True | Enable/disable email alerts |
| `SMTP_SERVER` | smtp.gmail.com | SMTP server address |
| `SMTP_PORT` | 587 | SMTP port (587 for TLS, 465 for SSL) |

## Logs

All activity is logged to `resource_tracker.log`. Example log output:

```
2026-04-15 10:30:00 - monitor - INFO - CPU Usage: 45.2%
2026-04-15 10:30:01 - monitor - INFO - RAM Usage: 67.8%
2026-04-15 10:30:01 - __main__ - INFO - Resource check complete - CPU: 45.2%, RAM: 67.8%
```
