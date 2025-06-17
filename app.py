# app.py
import schedule
import time
import asyncio
import threading
import config
import os
from services.export_service import ExportService
from data_sources.google_sheet_source import GoogleSheetSource
from data_processors.text_converter_processor import TextConverterProcessor
from data_destinations.excel_destination import ExcelDestination
from actions.playwright_action import PlaywrightAction
from telegram_bot import setup_bot, send_notification, send_documents
from config_manager import ConfigManager

# --- HÀM ASYNC GOM TÁC VỤ TELEGRAM (ĐÃ CẬP NHẬT) ---
async def post_job_actions_async(summary_message: str, dir_to_scan: str | None, target_user_id: int):
    """
    Thực hiện tất cả hành động bất đồng bộ sau khi job chạy xong và gửi tới đúng người dùng.
    """
    # Thay đổi 1: Gửi tin nhắn tóm tắt tới người dùng mục tiêu
    await send_notification(summary_message, user_telegram_id=target_user_id)
    
    # Thay đổi 2: Gửi các tài liệu từ thư mục làm việc tới người dùng mục tiêu
    if dir_to_scan:
        await send_documents(dir_to_scan, user_telegram_id=target_user_id)


def run_export_job(telegram_id: int):
    """
    Hàm logic chính, đã được cập nhật để xử lý thông báo cá nhân và thư mục làm việc động.
    """
    print(f"\n================  Bắt đầu tác vụ cho User ID: {telegram_id} ================")
    
    config_mgr = ConfigManager()
    
    # 1. Lấy thông tin đăng nhập của người dùng
    user_credentials = config_mgr.get_user_credentials(telegram_id)
    if not user_credentials:
        # Thay đổi 3: Gửi thông báo lỗi về cho đúng người dùng
        asyncio.run(send_notification(f"⚠️ Không thể tìm thấy thông tin đăng nhập của bạn.", user_telegram_id=telegram_id))
        return
    web_username, web_password = user_credentials

    # 2. Lấy danh sách các sheet của người dùng
    user_sheets = config_mgr.get_user_sheets(telegram_id)
    if not user_sheets:
        asyncio.run(send_notification(f"⚠️ Không tìm thấy tác vụ nào được cấu hình cho bạn.", user_telegram_id=telegram_id))
        return

    success_count = 0
    fail_count = 0
    total_sheets = len(user_sheets)
    # Thay đổi 4: Chỉ cần một biến để lưu thư mục làm việc cuối cùng
    last_workspace_dir = None

    # 3. Lặp qua từng sheet và thực thi
    for i, sheet_config in enumerate(user_sheets):
        spreadsheet_name = sheet_config.get("spreadsheet_name", "Không tên")
        print(f"\n--- Xử lý sheet {i+1}/{total_sheets}: {spreadsheet_name} ---")
        
        # Thay đổi 5: Tạo destination và lấy đường dẫn thư mục làm việc ngay từ đầu
        # Điều này đảm bảo dù thành công hay thất bại, ta vẫn biết nơi để tìm file kết quả/lỗi
        destination = ExcelDestination(
            base_path='workspace',
            telegram_id=telegram_id,
            spreadsheet_name=sheet_config['spreadsheet_name']
        )
        workspace_dir = destination.get_dir() # Lấy đường dẫn workspace, ví dụ: 'workspace/123/2025-06-17...'
        last_workspace_dir = workspace_dir # Cập nhật thư mục làm việc cuối cùng

        try:
            source = GoogleSheetSource(
                service_account_file=config.SERVICE_ACCOUNT_FILE,
                sheet_name=sheet_config['spreadsheet_name'],
                worksheet_name=sheet_config['worksheet_name']
            )
            processor = TextConverterProcessor()
            
            post_action = None
            if config.WEB_AUTOMATION_ENABLED:
                post_action = PlaywrightAction(
                    login_url=config.COMMON_LOGIN_URL,
                    import_url=config.IMPORT_URL,
                    username=web_username,
                    password=web_password,
                    locators=config.LOCATORS
                )
                # Truyền đường dẫn thư mục làm việc vào action để lưu ảnh chụp màn hình đúng chỗ
                post_action.set_screenshot_folder(workspace_dir)

            service = ExportService(source, processor, destination, post_action)
            service.run()
            success_count += 1

        except Exception as e:
            print(f"💥 LỖI khi xử lý sheet '{spreadsheet_name}': {e}")
            fail_count += 1

    # 4. Gửi báo cáo và file kết quả
    summary_message = (
        f"HOÀN THÀNH TÁC VỤ\n\n"
        f"- ID Người dùng: {telegram_id}\n"
        f"- Thành công: {success_count}/{total_sheets}\n"
        f"- Thất bại: {fail_count}/{total_sheets}"
    )

    # Thay đổi 6: Gọi hàm async wrapper một lần duy nhất với các tham số đã được cập nhật
    try:    
        asyncio.run(post_job_actions_async(
            summary_message=summary_message,
            dir_to_scan=last_workspace_dir,
            target_user_id=telegram_id
        ))
    except RuntimeError as e:
        print(f"Lỗi khi chạy post-job actions: {e}. Thử tạo event loop mới.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(post_job_actions_async(
            summary_message=summary_message,
            dir_to_scan=last_workspace_dir,
            target_user_id=telegram_id
        ))

    print(f"================ Kết thúc tác vụ cho User ID: {telegram_id} ================")

def run_scheduler():
    print("...Scheduler đang chạy trong nền...")
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    print("🚀 Khởi chạy ứng dụng Bot và Scheduler...")
    telegram_app = setup_bot()
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    print("...Bot đang lắng nghe lệnh...")
    telegram_app.run_polling()

if __name__ == "__main__":
    main()
