"""
Monitoring Camera - Main Application
Monitors CPU and RAM usage and sends email alerts when thresholds are exceeded.
"""

import json
import os
import time
import signal
import sys
import logging
import socket
import subprocess
from datetime import datetime

from monitor import ResourceMonitor
from email_alert import AlertManager, build_status_body
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def _load_state() -> dict:
    try:
        with open(config.STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state if isinstance(state, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state: dict) -> None:
    temp_path = f"{config.STATE_FILE}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, config.STATE_FILE)


class ResourceTracker:
    """Main application that monitors resources and triggers alerts."""

    def __init__(self):
        self.monitor = ResourceMonitor()
        self.alert_manager = AlertManager()
        self.running = False
        self.next_camera_check = 0
        self.next_status_email = time.monotonic() + config.STATUS_EMAIL_INTERVAL_SECONDS

    def check_resources(self):
        """Check system resources and send alerts if thresholds are exceeded."""
        logger.info("Checking system resources...")

        try:
            resources = self.monitor.check_resources()
            hostname = config.get_device_name()
            timestamp = resources["timestamp"]

            # Check CPU usage
            self.alert_manager.check_and_alert(
                resource_name="CPU",
                usage=resources["cpu_usage"],
                threshold=config.CPU_THRESHOLD,
                hostname=hostname,
                timestamp=timestamp,
                cpu_usage=resources["cpu_usage"],
                ram_usage=resources["ram_usage"],
                npu_usage=resources["npu_usage"],
            )

            # Check RAM usage
            self.alert_manager.check_and_alert(
                resource_name="RAM",
                usage=resources["ram_usage"],
                threshold=config.RAM_THRESHOLD,
                hostname=hostname,
                timestamp=timestamp,
                cpu_usage=resources["cpu_usage"],
                ram_usage=resources["ram_usage"],
                npu_usage=resources["npu_usage"],
            )

            # Check NPU cores (3 cores)
            for i, npu_load in enumerate(resources["npu_usage"]):
                self.alert_manager.check_and_alert(
                    resource_name=config.NPU_CORE_NAMES[i],
                    usage=npu_load,
                    threshold=config.NPU_THRESHOLD,
                    hostname=hostname,
                    timestamp=timestamp,
                    cpu_usage=resources["cpu_usage"],
                    ram_usage=resources["ram_usage"],
                    npu_usage=resources["npu_usage"],
                )

            logger.info(
                f"Resource check complete - "
                f"CPU: {resources['cpu_usage']:.1f}%, "
                f"RAM: {resources['ram_usage']:.1f}%, "
                f"NPU: [{resources['npu_usage'][0]:.1f}%, {resources['npu_usage'][1]:.1f}%, {resources['npu_usage'][2]:.1f}%]"
            )

        except Exception as e:
            logger.error(f"Error during resource check: {e}")

    @staticmethod
    def _ping_camera(ip_address: str) -> bool:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", ip_address],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError) as e:
            logger.warning(f"Failed to ping camera {ip_address}: {e}")
            return False

    def check_cameras(self):
        hostname = config.get_device_name()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unreachable = []
        cameras = config.get_cameras()

        logger.info("Checking camera connectivity...")
        for ip_address, camera_name in cameras.items():
            if self._ping_camera(ip_address):
                logger.info(f"Camera online: {camera_name} ({ip_address})")
            else:
                logger.warning(f"Camera offline: {camera_name} ({ip_address})")
                unreachable.append((ip_address, camera_name))

        self.alert_manager.check_camera_transitions(unreachable, hostname, timestamp)
        logger.info("Camera check complete")

    def send_boot_notification(self):
        hostname = config.get_device_name()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_active_time = _load_state().get("last_active_time", "Không xác định")
        self.alert_manager.send_boot_alert(hostname, timestamp, last_active_time)

    def update_heartbeat(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _save_state({"last_active_time": now})

    def send_status_notification(self):
        hostname = config.get_device_name()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = build_status_body(self.alert_manager, hostname, timestamp)
        self.alert_manager.email_alert.send_status_email(config.STATUS_SUBJECT, body, hostname, timestamp)

    def run(self):
        """Start the monitoring loop."""
        self.running = True
        logger.info("=" * 50)
        logger.info("Monitoring Camera Started")
        logger.info(f"Monitoring interval: {config.MONITORING_INTERVAL_SECONDS}s")
        logger.info(f"CPU threshold: {config.CPU_THRESHOLD}%")
        logger.info(f"RAM threshold: {config.RAM_THRESHOLD}%")
        logger.info(f"NPU threshold: {config.NPU_THRESHOLD}% (per core)")
        logger.info(f"Camera ping interval: {config.CAMERA_PING_INTERVAL_SECONDS}s")
        logger.info("=" * 50)
        self.send_boot_notification()

        while self.running:
            self.check_resources()
            now = time.monotonic()
            if now >= self.next_camera_check:
                self.check_cameras()
                self.next_camera_check = now + config.CAMERA_PING_INTERVAL_SECONDS
            if now >= self.next_status_email:
                self.send_status_notification()
                self.next_status_email = now + config.STATUS_EMAIL_INTERVAL_SECONDS
            self.update_heartbeat()
            logger.info(f"Sleeping for {config.MONITORING_INTERVAL_SECONDS} seconds...")
            time.sleep(config.MONITORING_INTERVAL_SECONDS)

    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
        self.next_camera_check = 0
        self.next_status_email = 0
        logger.info("Monitoring Camera stopped.")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("Received shutdown signal...")
    tracker.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    tracker = ResourceTracker()

    try:
        tracker.run()
    except KeyboardInterrupt:
        tracker.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
