# Monitoring Camera

Python service that monitors CPU, RAM, NPU, and configured cameras. It sends SMTP email alerts for resource threshold breaches, camera down/up transitions, boot events, and periodic status reports.

## Features

- **Resource monitoring**: Tracks CPU, RAM, and RKNN NPU usage.
- **Camera monitoring**: Pings configured cameras and alerts only on down/up transitions.
- **Email alerts**: Sends HTML SMTP notifications for resource alerts, camera status changes, boot events, and periodic status reports.
- **Alert cooldowns**: Repeats persistent high-usage alerts at most once per resource cooldown window.
- **Hot-reload JSON config**: Reloads camera and recipient lists without restarting the service.
- **Logging**: Writes checks and alerts to `resource_tracker.log`.

## Project Structure

```text
monitoring-camera/
├── main.py                 # Main service loop
├── monitor.py              # CPU, RAM, and NPU monitoring
├── email_alert.py          # Email alerts and camera transition state
├── config.py               # Static settings and JSON config loaders
├── cameras.json            # Hot-reloaded camera IP/name map
├── recipient_emails.json   # Hot-reloaded recipient list
├── test_email.py           # Manual SMTP test script
├── requirements.txt        # Python dependencies
└── resource_tracker.log    # Runtime log file
```

## Installation

```bash
pip install -r requirements.txt
```

Create `.env` with SMTP credentials:

```bash
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-password-or-app-password
```

## Usage

Run service:

```bash
python main.py
```

Run SMTP smoke test:

```bash
python test_email.py
```

Stop service with `Ctrl+C`.

## Configuration

Static settings live in `config.py`.

| Setting | Current Default | Description |
|---------|-----------------|-------------|
| `MONITORING_INTERVAL_SECONDS` | `60` | Seconds between resource checks |
| `CAMERA_PING_INTERVAL_SECONDS` | `600` | Seconds between camera ping checks |
| `CPU_THRESHOLD` | `70` | CPU alert threshold (%) |
| `RAM_THRESHOLD` | `70` | RAM alert threshold (%) |
| `NPU_THRESHOLD` | `90` | NPU per-core alert threshold (%) |
| `ALERT_COOLDOWN_SECONDS` | `1800` | Minimum seconds between repeated alerts for same resource |
| `STATUS_EMAIL_INTERVAL_SECONDS` | `21600` | Seconds between periodic status reports |
| `EMAIL_ENABLED` | `True` | Enable/disable email sends |
| `SMTP_SERVER` | `smtp.office365.com` | SMTP server address |
| `SMTP_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | Use SMTP + STARTTLS when true, SMTP_SSL when false |

## Hot-Reload JSON Files

Edit `recipient_emails.json` to change email recipients without restart:

```json
[
  "admin@example.com",
  "ops@example.com"
]
```

Edit `cameras.json` to change monitored cameras without restart:

```json
{
  "192.168.1.103": "Camera 1",
  "192.168.1.104": "Camera 2"
}
```

If a JSON file is temporarily invalid while being edited, the service logs a warning and keeps using the last valid version. When the file becomes valid again, the next check/email send reloads it.

When a camera is removed from `cameras.json`, stale in-memory camera status for that IP is pruned on the next camera transition check.

## NPU Load Sources

NPU usage is read in this order:

1. `NPU_DEBUG_LOAD_PATH` direct read, then `sudo -n cat` fallback
2. `NPU_LEGACY_CORE_PATHS` per-core sysfs paths
3. `NPU_DEVFREQ_LOAD_PATH` aggregate load replicated across 3 cores

If no NPU source is available, usage falls back to `[0.0, 0.0, 0.0]`.

## Logs

All activity is logged to `resource_tracker.log`. Example:

```text
2026-04-15 10:30:00 - monitor - INFO - CPU Usage: 45.2%
2026-04-15 10:30:01 - monitor - INFO - RAM Usage: 67.8%
2026-04-15 10:30:01 - __main__ - INFO - Resource check complete - CPU: 45.2%, RAM: 67.8%, NPU: [0.0%, 0.0%, 0.0%]
```
