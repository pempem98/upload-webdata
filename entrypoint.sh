#!/bin/sh

# Thoát ngay lập tức nếu một lệnh nào đó thất bại
set -e

# In ra thông báo bắt đầu
echo "Starting application..."

# Chạy ứng dụng Python
# Dùng 'exec' để tiến trình Python thay thế tiến trình shell này.
exec python app.py
