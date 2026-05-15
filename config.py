# Resource Tracker Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Monitoring Settings
MONITORING_INTERVAL_SECONDS = 60
CAMERA_PING_INTERVAL_SECONDS = 10 * 60
CPU_THRESHOLD = 70  # percent
RAM_THRESHOLD = 70  # percentsondn
NPU_THRESHOLD = 90  # percent (per core)
STATUS_EMAIL_INTERVAL_SECONDS = 6 * 60 * 60
DISPLAY_HOSTNAME = "AIBOX Cảng Gia Vũ - Hải Phòng"

CAMERAS = {
    "192.168.1.103": "Cam nhìn băng truyền",
    "192.168.1.34": "Cam nhìn cẩu hành từ tàu",
    "192.168.1.101": "Cam nhìn khoang hàng trên xe",
    "192.168.1.105": "Cam nhìn cao trên cân",
    "192.168.1.102": "Cam nhìn tréo cân",
    "192.168.1.107": "Cam nhìn biển xe trên cân 1",
    "192.168.1.100": "Cam nhìn biển xe trên cân 2",
}

# Email Settings
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
EMAIL_USE_TLS = True
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECIPIENT_EMAILS = [
    "sondn@vns.ai.vn",
    "huylq@vns.ai.vn",
]

# Email Content
EMAIL_SUBJECT_ALERT = "[CẢNH BÁO] Tài nguyên vượt ngưỡng - AIBOX Cảng Gia Vũ - Hải Phòng"
EMAIL_BODY_TEMPLATE = """
<html><body style="font-family:Arial,sans-serif;color:#1f2937;">
<h2 style="color:#b91c1c;">Cảnh báo tài nguyên vượt ngưỡng</h2>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thiết bị</td><td style="border:1px solid #ddd;padding:8px;">{hostname}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thời gian</td><td style="border:1px solid #ddd;padding:8px;color:#b91c1c;font-weight:bold;">{timestamp}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Tài nguyên</td><td style="border:1px solid #ddd;padding:8px;color:#b91c1c;font-weight:bold;">{resource_name}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Mức sử dụng hiện tại</td><td style="border:1px solid #ddd;padding:8px;color:#b91c1c;font-weight:bold;">{usage:.1f}%</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Ngưỡng cảnh báo</td><td style="border:1px solid #ddd;padding:8px;">{threshold}%</td></tr>
</table>
<h3>Trạng thái tài nguyên tại thời điểm cảnh báo</h3>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr style="background:#f3f4f6;"><th style="border:1px solid #ddd;padding:8px;text-align:left;">Tài nguyên</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">Mức sử dụng</th></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;">CPU</td><td style="border:1px solid #ddd;padding:8px;">{cpu_usage:.1f}%</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;">RAM</td><td style="border:1px solid #ddd;padding:8px;">{ram_usage:.1f}%</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;">NPU Core 0</td><td style="border:1px solid #ddd;padding:8px;">{npu_core_0:.1f}%</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;">NPU Core 1</td><td style="border:1px solid #ddd;padding:8px;">{npu_core_1:.1f}%</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;">NPU Core 2</td><td style="border:1px solid #ddd;padding:8px;">{npu_core_2:.1f}%</td></tr>
</table>
<p style="color:#b91c1c;font-weight:bold;">Vui lòng kiểm tra ngay.</p>
</body></html>
"""
CAMERA_DOWN_SUBJECT = "[CẢNH BÁO] Camera mất kết nối - AIBOX Cảng Gia Vũ - Hải Phòng"
CAMERA_DOWN_BODY_TEMPLATE = """
<html><body style="font-family:Arial,sans-serif;color:#1f2937;">
<h2 style="color:#b91c1c;">Camera mất kết nối</h2>
<p><b>Thiết bị:</b> {hostname}</p>
<p><b>Thời gian:</b> {timestamp}</p>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr style="background:#f3f4f6;"><th style="border:1px solid #ddd;padding:8px;text-align:left;">Trạng thái</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">Tên camera</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">IP</th></tr>
  {camera_rows}
</table>
<p style="color:#b91c1c;font-weight:bold;">Vui lòng kiểm tra ngay.</p>
</body></html>
"""
CAMERA_UP_SUBJECT = "[KHÔI PHỤC] Camera đã kết nối lại - AIBOX Cảng Gia Vũ - Hải Phòng"
CAMERA_UP_BODY_TEMPLATE = """
<html><body style="font-family:Arial,sans-serif;color:#1f2937;">
<h2 style="color:#15803d;">Camera đã kết nối lại</h2>
<p><b>Thiết bị:</b> {hostname}</p>
<p><b>Thời gian:</b> {timestamp}</p>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr style="background:#f3f4f6;"><th style="border:1px solid #ddd;padding:8px;text-align:left;">Trạng thái</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">Tên camera</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">IP</th></tr>
  {camera_rows}
</table>
</body></html>
"""
BOOT_SUBJECT = "[THÔNG TIN] Máy vừa khởi động lại - AIBOX Cảng Gia Vũ - Hải Phòng"
BOOT_BODY_TEMPLATE = """
<html><body style="font-family:Arial,sans-serif;color:#1f2937;">
<h2 style="color:#2563eb;">Máy vừa khởi động lại</h2>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thiết bị</td><td style="border:1px solid #ddd;padding:8px;">{hostname}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thời gian chết</td><td style="border:1px solid #ddd;padding:8px;color:#b91c1c;font-weight:bold;">{timestamp}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thời gian khởi động lại</td><td style="border:1px solid #ddd;padding:8px;color:#15803d;font-weight:bold;">{boot_time}</td></tr>
</table>
</body></html>
"""

STATUS_SUBJECT = "[BÁO CÁO] Trạng thái định kỳ - AIBOX Cảng Gia Vũ - Hải Phòng"
STATUS_BODY_TEMPLATE = """
<html><body style="font-family:Arial,sans-serif;color:#1f2937;">
<h2 style="color:#2563eb;">Báo cáo trạng thái định kỳ</h2>
<table style="border-collapse:collapse;width:100%;max-width:760px;margin-bottom:16px;">
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">AIBOX</td><td style="border:1px solid #ddd;padding:8px;">{hostname}</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Trạng thái AIBOX</td><td style="border:1px solid #ddd;padding:8px;color:#15803d;font-weight:bold;">Đang hoạt động</td></tr>
  <tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">Thời gian</td><td style="border:1px solid #ddd;padding:8px;color:#b91c1c;font-weight:bold;">{timestamp}</td></tr>
</table>
<h3>Trạng thái camera</h3>
<table style="border-collapse:collapse;width:100%;max-width:760px;">
  <tr style="background:#f3f4f6;"><th style="border:1px solid #ddd;padding:8px;text-align:left;">Trạng thái</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">Tên camera</th><th style="border:1px solid #ddd;padding:8px;text-align:left;">IP</th></tr>
  {camera_rows}
</table>
</body></html>
"""

# NPU Settings
NPU_CORE_NAMES = ["NPU Core 0", "NPU Core 1", "NPU Core 2"]
NPU_DEBUG_LOAD_PATH = "/sys/kernel/debug/rknpu/load"
NPU_DEVFREQ_LOAD_PATH = "/sys/devices/platform/fdab0000.npu/devfreq/fdab0000.npu/load"
NPU_LEGACY_CORE_PATHS = [
    "/sys/class/misc/rknpu/load0",
    "/sys/class/misc/rknpu/load1",
    "/sys/class/misc/rknpu/load2",
]

# Logging
LOG_FILE = "resource_tracker.log"
LOG_LEVEL = "INFO"
