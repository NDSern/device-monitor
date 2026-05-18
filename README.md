# Monitoring Camera

Dịch vụ Python dùng để giám sát CPU, RAM, NPU và danh sách camera đã cấu hình. Ứng dụng gửi email SMTP khi tài nguyên vượt ngưỡng, camera mất/kết nối lại, thiết bị khởi động lại, và gửi báo cáo trạng thái định kỳ.

## Tính Năng

- **Giám sát tài nguyên**: Theo dõi CPU, RAM và mức tải RKNN NPU.
- **Giám sát camera**: Ping các camera đã cấu hình và chỉ cảnh báo khi trạng thái chuyển từ online sang offline hoặc ngược lại.
- **Giám sát aibox**: Ping các aibox đã cấu hình và cảnh báo khi aibox chuyển trạng thái từ online sang offline hoặc ngược lại.
- **Cảnh báo email**: Gửi email HTML cho cảnh báo tài nguyên, thay đổi trạng thái camera, sự kiện khởi động lại và báo cáo định kỳ.
- **Giới hạn lặp cảnh báo**: Với tài nguyên vẫn vượt ngưỡng, mỗi tài nguyên chỉ gửi lại cảnh báo sau khoảng cooldown.
- **Cấu hình JSON hot-reload**: Tự đọc lại danh sách camera, người nhận email và tên thiết bị mà không cần khởi động lại dịch vụ.
- **Ghi log**: Ghi toàn bộ lần kiểm tra và cảnh báo vào `resource_tracker.log`.

## Cho Người Giám Sát

[Doc Cho Team Giám Sát](https://vnscorporation-my.sharepoint.com/:w:/g/personal/sondn_vns_ai_vn/IQAwJua1lXNpRaaAwkkFxp5_ARXw7ijjgKObLp9VEazuJeg?e=aoco1a)

## Cho Repo Maintainer

### Cài Đặt

```bash
pip install -r requirements.txt
```

Tạo file `.env` chứa thông tin đăng nhập SMTP:

```bash
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-password-or-app-password
```

### Sử Dụng

Chạy dịch vụ:

```bash
python main.py
```

Gửi email kiểm tra SMTP:

```bash
python test_email.py
```

Dừng dịch vụ bằng `Ctrl+C`.

### Cấu Hình

Các thiết lập tĩnh nằm trong `config/config.py`.

| Thiết lập | Giá trị mặc định | Mô tả |
|-----------|------------------|-------|
| `MONITORING_INTERVAL_SECONDS` | `60` | Số giây giữa các lần kiểm tra tài nguyên |
| `CAMERA_PING_INTERVAL_SECONDS` | `600` | Số giây giữa các lần ping camera |
| `CPU_THRESHOLD` | `70` | Ngưỡng cảnh báo CPU (%) |
| `RAM_THRESHOLD` | `70` | Ngưỡng cảnh báo RAM (%) |
| `NPU_THRESHOLD` | `90` | Ngưỡng cảnh báo từng core NPU (%) |
| `ALERT_COOLDOWN_SECONDS` | `1800` | Thời gian tối thiểu giữa các email cảnh báo lặp lại cho cùng một tài nguyên |
| `STATUS_EMAIL_INTERVAL_SECONDS` | `21600` | Số giây giữa các email báo cáo trạng thái định kỳ |
| `EMAIL_ENABLED` | `True` | Bật/tắt gửi email |
| `SMTP_SERVER` | `smtp.office365.com` | Địa chỉ SMTP server |
| `SMTP_PORT` | `587` | Cổng SMTP |
| `EMAIL_USE_TLS` | `True` | `True` dùng SMTP + STARTTLS, `False` dùng SMTP_SSL |

### File JSON Hot-Reload

Sửa `recipient_emails.json` để thay đổi danh sách người nhận email mà không cần khởi động lại:
Đường dẫn: `config/recipient_emails.json`

```json
[
  "admin@example.com",
  "ops@example.com"
]
```

Sửa `cameras.json` để thay đổi danh sách camera giám sát mà không cần khởi động lại:
Đường dẫn: `config/cameras.json`

```json
{
  "192.168.1.103": "Camera 1",
  "192.168.1.104": "Camera 2"
}
```

Sửa `device_name.json` để thay đổi tên thiết bị hiển thị mà không cần khởi động lại:

Đường dẫn: `config/device_name.json`

```json
{
  "device_name": "AIBOX Cảng Gia Vũ - Hải Phòng"
}
```

Nếu một file JSON tạm thời không hợp lệ trong lúc đang sửa, dịch vụ sẽ ghi cảnh báo vào log và tiếp tục dùng phiên bản hợp lệ gần nhất. Khi file hợp lệ trở lại, lần kiểm tra hoặc lần gửi email tiếp theo sẽ tự đọc lại nội dung mới.

Khi một camera bị xóa khỏi `config/cameras.json`, trạng thái camera cũ trong bộ nhớ sẽ được xóa ở lần kiểm tra chuyển trạng thái camera tiếp theo.

### Nguồn Đọc Tải NPU

Ứng dụng đọc mức tải NPU theo thứ tự sau:

1. Đọc trực tiếp `NPU_DEBUG_LOAD_PATH`, sau đó fallback sang `sudo -n cat`.
2. Đọc từng core từ `NPU_LEGACY_CORE_PATHS`.
3. Đọc tải tổng từ `NPU_DEVFREQ_LOAD_PATH` và nhân ra 3 core.

Nếu không đọc được nguồn NPU nào, giá trị tải sẽ fallback về `[0.0, 0.0, 0.0]`.

### Log

Toàn bộ hoạt động được ghi vào `resource_tracker.log`. Ví dụ:

```text
2026-04-15 10:30:00 - monitor - INFO - CPU Usage: 45.2%
2026-04-15 10:30:01 - monitor - INFO - RAM Usage: 67.8%
2026-04-15 10:30:01 - __main__ - INFO - Resource check complete - CPU: 45.2%, RAM: 67.8%, NPU: [0.0%, 0.0%, 0.0%]
```
