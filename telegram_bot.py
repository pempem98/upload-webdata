# telegram_bot.py
import schedule
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import config

bot_instance = None
chat_id = config.TELEGRAM_CHAT_ID
TIME_INPUT = 0

async def send_notification(message: str):
    if bot_instance and chat_id:
        try:
            await bot_instance.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Lỗi khi gửi thông báo Telegram: {e}")

def authorized(update: Update) -> bool:
    return update.effective_user.id in config.TELEGRAM_ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text(
        "Chào mừng! Tôi là bot tự động hóa.\n"
        "Các lệnh có sẵn:\n"
        "/run - Chạy tác vụ ngay lập tức.\n"
        "/schedule - Lập lịch chạy tác vụ hàng ngày.\n"
        "/status - Xem các lịch đã đặt."
    )

async def run_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ Nhận lệnh! Bắt đầu chạy tác vụ ngay bây giờ...")
    from app import run_export_job
    threading.Thread(target=run_export_job).start()

async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("Vui lòng nhập thời gian bạn muốn chạy tác vụ hàng ngày (định dạng HH:MM, ví dụ: 08:30):")
    return TIME_INPUT

async def schedule_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from app import run_export_job
    user_time = update.message.text
    try:
        schedule.every().day.at(user_time).do(run_export_job).tag(f"daily_{user_time}")
        await update.message.reply_text(f"✅ Đã đặt lịch thành công! Tác vụ sẽ chạy vào lúc {user_time} mỗi ngày.")
        print(f"Lịch mới được đặt: hàng ngày lúc {user_time}")
    except Exception as e:
        await update.message.reply_text(f"❌ Định dạng thời gian không hợp lệ. Vui lòng thử lại. Lỗi: {e}")
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    jobs = schedule.get_jobs()
    if not jobs:
        await update.message.reply_text("Hiện không có lịch nào được đặt.")
    else:
        status_text = "🗓️ Các lịch đang hoạt động:\n"
        for job in jobs:
            status_text += f"- {job.tags}\n"
        await update.message.reply_text(status_text)

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Đã hủy thao tác.")
    return ConversationHandler.END

def setup_bot():
    global bot_instance
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    bot_instance = application.bot

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("schedule", schedule_start)],
        states={TIME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_received)]},
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_now))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(conv_handler)
    
    return application
