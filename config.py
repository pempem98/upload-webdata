# config.py
import os

# Cấu hình chung cho file
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', 'credentials.json')

# --- CẤU HÌNH CHUNG CHO TỰ ĐỘNG HÓA WEB ---
WEB_AUTOMATION_ENABLED = os.getenv('WEB_AUTOMATION_ENABLED', 'True').lower() == 'true'

# URL đăng nhập và URL import
COMMON_LOGIN_URL = os.getenv('COMMON_LOGIN_URL', "https://admin.mayhomes.vn/web/login")
IMPORT_URL = os.getenv('IMPORT_URL', "https://admin.mayhomes.vn/web#model=product.template&action=import")

# Locators cho automation (dùng chung cho các tác vụ)
LOCATORS = {
    'username_field': '#login',
    'password_field': '#password',
    'login_button': 'button.btn.btn-primary',
    'post_login_element': 'body > header > nav > div > div > button > img',
    'close_warning': 'button.btn-close',
    'import_input': 'input.oe_import_file',
    'import_button': 'button.btn.o_import_import.o_import_import_full',
    'batch_limit': '#oe_import_batch_limit',
    'loading_spin': 'div.o_import_progress_dialog',
    'import_alert': 'div.oe_import_report.alert',
}

# --- CẤU HÌNH CHO TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Đọc danh sách admin ID từ biến môi trường, phân tách bằng dấu phẩy
admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS', "")
TELEGRAM_ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]

# Kiểm tra các biến môi trường quan trọng
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Lỗi: Biến môi trường TELEGRAM_BOT_TOKEN chưa được thiết lập.")
if not TELEGRAM_ADMIN_IDS:
    raise ValueError("Lỗi: Biến môi trường TELEGRAM_ADMIN_IDS chưa được thiết lập.")