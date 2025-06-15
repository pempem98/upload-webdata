# config.py

# Cấu hình cho đường dẫn và tên file
SERVICE_ACCOUNT_FILE = 'credentials.json'
OUTPUT_FILENAME = 'DD UP WEB.xlsx'

# Cấu hình cho Google Sheet
GOOGLE_SHEET_NAME = 'DD UP WEB'
WORKSHEET_NAME = 'Căn hộ cao tầng'

# --- CẤU HÌNH CHO TỰ ĐỘNG HÓA WEB ---
WEB_AUTOMATION_ENABLED = True

LOGIN_URL = "https://admin.mayhomes.vn/web/login"
IMPORT_URL = "https://admin.mayhomes.vn/web#model=product.template&action=import"
USERNAME = "lethuhien@gmail.com"
PASSWORD = "123456"

# Locators cho automation (sử dụng CSS Selectors)
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
# Danh sách ID của admin có quyền sử dụng bot
TELEGRAM_ADMIN_IDS = [5749118184]
