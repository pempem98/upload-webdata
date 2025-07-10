# Dockerfile
# Sử dụng Python 3.11 base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt tiện ích dos2unix để xử lý ký tự xuống dòng (CRLF -> LF)
# và các thư viện cần thiết cho Playwright
RUN apt-get update && \
    apt-get install -y dos2unix libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Sao chép file requirements.txt trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt cho Playwright
RUN playwright install --with-deps chromium

# Sao chép toàn bộ mã nguồn của ứng dụng vào container
COPY . .

# Chuyển đổi định dạng file entrypoint.sh sang Unix (LF)
RUN dos2unix /app/entrypoint.sh

# Cấp quyền thực thi cho entrypoint script
RUN chmod +x /app/entrypoint.sh

# Thiết lập entrypoint để chạy ứng dụng
ENTRYPOINT ["/app/entrypoint.sh"]