from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from interfaces.post_export_action import IPostExportAction
import os

class PlaywrightAction(IPostExportAction):
    def __init__(self, login_url: str, import_url: str, username: str, password: str, locators: dict):
        self.login_url = login_url
        self.import_url = import_url
        self.username = username
        self.password = password
        self.locators = locators
        self.screenshot_folder = '.'

    def set_screenshot_folder(self, dir: str):
        self.screenshot_folder = dir

    def execute(self, file_path: str): # file_path được truyền vào từ service
        print(f"\n▶️ Bắt đầu hành động tự động hóa web...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                print(f"🌍 Đang điều hướng tới: {self.login_url}")
                page.goto(self.login_url, timeout=60000)
                print(f"🔑 Đăng nhập với tài khoản: {self.username}")
                page.fill(self.locators['username_field'], self.username)
                page.fill(self.locators['password_field'], self.password)
                page.click(self.locators['login_button'])
                page.wait_for_selector(self.locators['post_login_element'], timeout=30000)
                print("✅ Đăng nhập thành công!")
                if page.is_visible(self.locators['close_warning']):
                    page.click(self.locators['close_warning'])

                print(f"🌍 Đang điều hướng tới trang Import: {self.import_url}")
                page.goto(self.import_url, timeout=60000)

                print(f"⬆️ Chuẩn bị upload file: {file_path}")
                page.locator(self.locators['import_input']).set_input_files(file_path)

                print(f"Cài Batch Limit về 1000")
                page.fill(self.locators['batch_limit'], "1000")

                print(f"Bắt đầu đẩy dữ liệu...")
                page.click(self.locators['import_button'])

                print("⏳ Chờ quá trình import hoàn tất...")
                # import time
                # time.sleep(10)
                loading_spin = page.locator(self.locators['loading_spin'])
                expect(loading_spin).not_to_be_visible(timeout=600000)

                # Kiểm tra thông báo kết quả
                alert_boxes = page.locator(self.locators['import_alert']).all()
                if len(alert_boxes):
                    alert_text = alert_boxes[0].text_content().replace('\n', ' ').replace('  ', '')
                    print(f"📢 Thông báo kết quả: {alert_text}")
                    raise Exception(f"Lỗi import: {alert_text}")
                
                print("✅ Import thành công!")
                page.screenshot(path=os.path.join(self.screenshot_folder, 'success.png'))

            except PlaywrightTimeoutError as e:
                error_message = f"Lỗi Timeout: {e}"
                page.screenshot(path=os.path.join(self.screenshot_folder, 'timeout_error.png'))
                raise Exception(error_message)
            except Exception as e:
                page.screenshot(path=os.path.join(self.screenshot_folder, 'unknown_error.png'))
                raise e # Ném lại lỗi để app.py bắt được
            finally:
                browser.close()
                print("🚪 Đã đóng trình duyệt.")