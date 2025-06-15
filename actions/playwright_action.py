import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import IMPORT_URL, OUTPUT_FILENAME
from interfaces.post_export_action import IPostExportAction

class PlaywrightAction(IPostExportAction):
    def __init__(self, login_url: str, username: str, password: str, locators: dict):
        self.login_url = login_url
        self.username = username
        self.password = password
        self.locators = locators
        self.import_url = IMPORT_URL
        self.max_wait_turn = 15
        self.file_name = OUTPUT_FILENAME

    def execute(self, file_path: str):
        print(f"\n▶️ Bắt đầu hành động tự động hóa web...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                print(f"🌍 Đang điều hướng tới: {self.login_url}")
                page.goto(self.login_url, timeout=60000)
                print("🔑 Đang thực hiện đăng nhập...")
                page.fill(self.locators['username_field'], self.username)
                page.fill(self.locators['password_field'], self.password)
                page.click(self.locators['login_button'])
                print("⏳ Chờ trang dashboard sau khi đăng nhập...")
                page.wait_for_selector(self.locators['post_login_element'], timeout=30000)
                print("✅ Đăng nhập thành công!")
                print("⏳ Kiểm tra và tắt cảnh báo nếu có...")
                if page.is_visible(self.locators['close_warning'], timeout=30000):
                    page.click(self.locators['close_warning'])
                print(f"🌍 Đang điều hướng tới: {self.import_url}")
                page.goto(self.import_url, timeout=60000)
                print("🖱️ Thực hiện các thao tác nhập liệu...")
                page.locator(self.locators['import_input']).set_input_files(self.file_name)
                page.fill(self.locators['batch_limit'], '1000')
                page.click(self.locators['import_button'])
                current_turn = 0
                while current_turn <= (self.max_wait_turn):
                    time.sleep(60)
                    page.screenshot(path=f'loading_screenshot-{current_turn}.png')
                    if not page.is_visible(self.locators['loading_spin'], timeout=10000):
                        break;
                    current_turn += 1
                if not page.is_visible(self.locators['import_alert']):
                    print("✅ Hoàn thành các thao tác trên web.")
                    page.screenshot(path='success_screenshot.png')
                else:
                    print("❌ Lỗi khi nhập tập tin.")
                    page.screenshot(path='error_screenshot.png')
                time.sleep(3)
                return "Tự động hóa web với Playwright thành công!"
            except PlaywrightTimeoutError as e:
                error_message = f"Lỗi Timeout: Không thể tìm thấy element trong thời gian quy định. {e}"
                print(f"❌ {error_message}")
                page.screenshot(path='error_screenshot.png')
                raise Exception(error_message)
            except Exception as e:
                print(f"❌ Lỗi trong quá trình tự động hóa Playwright: {e}")
                raise
            finally:
                browser.close()
                print("🚪 Đã đóng trình duyệt.")
