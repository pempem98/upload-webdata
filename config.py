# config.py
# Cấu hình chung cho file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- CẤU HÌNH CHUNG CHO TỰ ĐỘNG HÓA WEB ---
WEB_AUTOMATION_ENABLED = True

# URL đăng nhập và URL import là cấu hình chung
COMMON_LOGIN_URL = "https://admin.mayhomes.vn/web/login"
IMPORT_URL = "https://admin.mayhomes.vn/web#model=product.template&action=import"

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
TELEGRAM_BOT_TOKEN = "7672970617:AAFecyaaMPSGoyLO-40_HyoAOOX-2WkKEO0"
TELEGRAM_CHAT_ID = "5749118184"
TELEGRAM_ADMIN_IDS = [5749118184]
