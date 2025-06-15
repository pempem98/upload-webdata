# app.py
import schedule
import time
import asyncio
import threading
import config
from services.export_service import ExportService
from data_sources.google_sheet_source import GoogleSheetSource
from data_processors.text_converter_processor import TextConverterProcessor
from data_destinations.excel_destination import ExcelDestination
from actions.playwright_action import PlaywrightAction
from telegram_bot import setup_bot, send_notification

def run_export_job():
    print("\n=============================================")
    print(f"⏰ Bắt đầu tác vụ vào lúc: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=============================================")
    
    try:
        source = GoogleSheetSource(
            service_account_file=config.SERVICE_ACCOUNT_FILE,
            sheet_name=config.GOOGLE_SHEET_NAME,
            worksheet_name=config.WORKSHEET_NAME
        )
        processor = TextConverterProcessor()
        destination = ExcelDestination(output_filename=config.OUTPUT_FILENAME)
        
        post_action = None
        if config.WEB_AUTOMATION_ENABLED:
            post_action = PlaywrightAction(
                login_url=config.LOGIN_URL,
                username=config.USERNAME,
                password=config.PASSWORD,
                locators=config.LOCATORS
            )

        service = ExportService(source, processor, destination, post_action)
        service.run()

        asyncio.run(send_notification("✅ Tác vụ đã hoàn thành thành công!"))

    except Exception as e:
        print(f"💥 LỖI NGHIÊM TRỌNG: {e}")
        asyncio.run(send_notification(f"❌ Tác vụ thất bại!\nLỗi: {e}"))

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
