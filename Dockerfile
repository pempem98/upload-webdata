# Stage 1: Chọn một base image Python gọn nhẹ
FROM python:3.11-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Tối ưu hóa cache: Copy và cài đặt requirements trước
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chạy lệnh cài đặt trình duyệt cho Playwright bên trong container
RUN playwright install --with-deps

# Copy file entrypoint vào và cấp quyền thực thi
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy toàn bộ code của ứng dụng vào thư mục làm việc trong container
COPY . .

# Chỉ định entrypoint để chạy khi container khởi động
ENTRYPOINT ["/app/entrypoint.sh"]
