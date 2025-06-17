# telegram_bot.py
import os
import schedule
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)
import config
from config_manager import ConfigManager

# --- BIẾN TOÀN CỤC VÀ CÁC HẰNG SỐ ---

bot_instance = None

# Định nghĩa các trạng thái cho ConversationHandler để quản lý các cuộc hội thoại
(
    # Trạng thái cho /schedule
    SCHEDULE_TIME,
    # Trạng thái cho /adduser
    ADDUSER_ID, ADDUSER_UNAME, ADDUSER_PASS, ADDUSER_ALIAS,
    # Trạng thái cho /addsheet
    ADDSHEET_ID, ADDSHEET_SNAME, ADDSHEET_WNAME,
    # Trạng thái cho /edituser
    EDITUSER_ID, EDITUSER_CHOOSE_FIELD, EDITUSER_GET_NEW_VALUE,
    # Trạng thái cho /deluser
    DELUSER_ID, DELUSER_CONFIRM,
    # Trạng thái cho /editsheet
    EDITSHEET_USER_ID, EDITSHEET_CHOOSE_SHEET, EDITSHEET_CHOOSE_FIELD, EDITSHEET_GET_NEW_VALUE,
    # Trạng thái cho /delsheet
    DELSHEET_USER_ID, DELSHEET_CHOOSE_SHEET, DELSHEET_CONFIRM
) = range(20)


# --- CÁC HÀM TIỆN ÍCH VÀ KIỂM TRA QUYỀN ---

async def send_notification(message: str, user_telegram_id: int = None):
    """Gửi một tin nhắn văn bản tới người dùng cụ thể hoặc kênh admin mặc định."""
    # Ưu tiên gửi cho người dùng cụ thể nếu được cung cấp
    target_chat_id = user_telegram_id if user_telegram_id else config.TELEGRAM_CHAT_ID
    
    if bot_instance and target_chat_id:
        try:
            await bot_instance.send_message(chat_id=target_chat_id, text=message)
        except Exception as e:
            print(f"Lỗi khi gửi thông báo tới {target_chat_id}: {e}")

async def send_documents(dirpath: str, user_telegram_id: int):
    """Quét một thư mục và gửi các file .xlsx và .png tới người dùng cụ thể."""
    if not bot_instance:
        print("Lỗi: Bot chưa được khởi tạo.")
        return
    
    # Hàm này bắt buộc phải có user_telegram_id để gửi
    target_chat_id = user_telegram_id
    print(f"🔍 Quét thư mục '{dirpath}' để gửi file tới người dùng {target_chat_id}...")
    try:
        if not os.path.isdir(dirpath):
            # Gửi thông báo lỗi cho chính người dùng đó
            await send_notification(f"⚠️ Thư mục kết quả '{dirpath}' không tồn tại.", user_telegram_id=target_chat_id)
            return

        files_in_dir = os.listdir(dirpath)
        for filename in files_in_dir:
            full_path = os.path.join(dirpath, filename)
            if os.path.isfile(full_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    with open(full_path, 'rb') as photo_file:
                        await bot_instance.send_photo(chat_id=target_chat_id, photo=photo_file, caption=filename)
                elif filename.lower().endswith('.xlsx'):
                    with open(full_path, 'rb') as doc_file:
                        await bot_instance.send_document(chat_id=target_chat_id, document=doc_file, filename=filename, caption=filename)
    except Exception as e:
        await send_notification(f"❌ Đã có lỗi khi gửi tài liệu từ '{dirpath}': {e}", user_telegram_id=target_chat_id)

def is_admin(update: Update) -> bool:
    """Kiểm tra xem người dùng có phải là admin không (dựa trên config.py)."""
    return update.effective_user.id in config.TELEGRAM_ADMIN_IDS

def is_registered_user(update: Update) -> bool:
    """Kiểm tra xem người dùng có tồn tại trong database không."""
    return ConfigManager().user_exists(update.effective_user.id)


# --- CÁC HÀM XỬ LÝ LỆNH CƠ BẢN ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi tin nhắn chào mừng tùy theo vai trò của người dùng."""
    user = update.effective_user
    if is_admin(update):
        await update.message.reply_text(
            f"Chào mừng Quản trị viên {user.first_name}!\n\n"
            "**Lệnh cơ bản:**\n"
            "/run, /schedule, /status, /cancel\n\n"
            "**Quản lý người dùng:**\n"
            "/adduser, /edituser, /deluser\n\n"
            "**Quản lý tác vụ:**\n"
            "/addsheet, /editsheet, /delsheet",
            parse_mode='Markdown'
        )
    elif is_registered_user(update):
        await update.message.reply_text(
            f"Chào mừng {user.first_name}!\n"
            "Các lệnh có sẵn cho bạn:\n"
            "/run, /schedule, /status, /cancel"
        )
    else:
        await update.message.reply_text("❌ Bạn không có quyền truy cập hệ thống này.")

async def run_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kích hoạt chạy tác vụ ngay lập tức cho người dùng."""
    if not is_registered_user(update):
        await update.message.reply_text("❌ Bạn chưa được đăng ký trong hệ thống.")
        return

    user_id = update.effective_user.id
    await update.message.reply_text("⏳ Nhận lệnh! Bắt đầu chạy các tác vụ của bạn...")
    from app import run_export_job
    threading.Thread(target=run_export_job, args=(user_id,)).start()

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị các lịch đang hoạt động."""
    if not is_registered_user(update):
        await update.message.reply_text("❌ Bạn chưa được đăng ký trong hệ thống.")
        return
    jobs = schedule.get_jobs()
    if not jobs:
        await update.message.reply_text("Hiện không có lịch nào được đặt.")
    else:
        status_text = "🗓️ Các lịch đang hoạt động:\n\n"
        for job in jobs:
            user_tag = next((tag for tag in job.tags if str(tag).startswith('user_')), "")
            time_tag = next((tag for tag in job.tags if str(tag).startswith('time_')), "")
            if user_tag and time_tag:
                 status_text += f"- User: `{user_tag.split('_')[1]}` lúc `{time_tag.split('_')[1]}` hàng ngày\n"
        await update.message.reply_text(status_text, parse_mode='Markdown')

async def cancel_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hủy tất cả các lịch đã đặt của người dùng gửi lệnh."""
    if not is_registered_user(update):
        await update.message.reply_text("❌ Bạn chưa được đăng ký trong hệ thống.")
        return
    
    user_id = update.effective_user.id
    user_tag = f"user_{user_id}"
    jobs_to_cancel = [job for job in schedule.get_jobs() if user_tag in job.tags]

    if not jobs_to_cancel:
        await update.message.reply_text("Bạn không có lịch nào đang hoạt động để huỷ.")
        return

    schedule.clear(user_tag)
    await update.message.reply_text(f"✅ Đã huỷ thành công {len(jobs_to_cancel)} lịch đã đặt của bạn.")


# --- QUY TRÌNH HỘI THOẠI: LẬP LỊCH (/schedule) ---

async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bắt đầu cuộc hội thoại đặt lịch."""
    if not is_registered_user(update):
        await update.message.reply_text("❌ Bạn chưa được đăng ký trong hệ thống.")
        return ConversationHandler.END
    await update.message.reply_text("Vui lòng nhập thời gian chạy hàng ngày (định dạng HH:MM):")
    return SCHEDULE_TIME

async def schedule_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Nhận thời gian và tạo lịch."""
    from app import run_export_job
    user_id = update.effective_user.id
    user_time = update.message.text
    try:
        schedule.every().day.at(user_time).do(run_export_job, telegram_id=user_id).tag(f"user_{user_id}", f"time_{user_time}")
        await update.message.reply_text(f"✅ Đã đặt lịch thành công lúc {user_time} mỗi ngày.")
    except schedule.ScheduleError:
        await update.message.reply_text(f"❌ Định dạng thời gian '{user_time}' không hợp lệ.")
    return ConversationHandler.END


# --- QUY TRÌNH HỘI THOẠI: QUẢN LÝ NGƯỜI DÙNG (ADMIN) ---

# === /adduser: Thêm người dùng mới ===
async def adduser_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update): return ConversationHandler.END
    await update.message.reply_text("Nhập ID Telegram của người dùng mới:")
    return ADDUSER_ID

async def adduser_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data['new_user_id'] = int(update.message.text)
        await update.message.reply_text("Nhập Tên đăng nhập web (email):")
        return ADDUSER_UNAME
    except ValueError:
        await update.message.reply_text("ID không hợp lệ. Vui lòng nhập số.")
        return ADDUSER_ID

async def adduser_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['web_username'] = update.message.text
    await update.message.reply_text("Nhập Mật khẩu web:")
    return ADDUSER_PASS

async def adduser_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['web_password'] = update.message.text
    await update.message.delete()
    await update.message.reply_text("Đã nhận mật khẩu (tin nhắn đã xóa). Nhập bí danh (alias) cho người dùng:")
    return ADDUSER_ALIAS

async def adduser_get_alias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user_alias'] = update.message.text
    ConfigManager().add_or_update_user(
        telegram_id=context.user_data['new_user_id'],
        web_username=context.user_data['web_username'],
        web_password=context.user_data['web_password'],
        user_alias=context.user_data['user_alias']
    )
    await update.message.reply_text(f"✅ Đã thêm/cập nhật người dùng: {context.user_data['user_alias']}")
    return ConversationHandler.END

# === /edituser: Sửa thông tin người dùng ===
async def edituser_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update): return ConversationHandler.END
    await update.message.reply_text("Nhập ID Telegram của người dùng bạn muốn sửa:")
    return EDITUSER_ID

async def edituser_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_id = int(update.message.text)
        user_info = ConfigManager().get_user(user_id)
        if not user_info:
            await update.message.reply_text("❌ Không tìm thấy người dùng.")
            return ConversationHandler.END
        
        context.user_data['edit_user_id'] = user_id
        keyboard = [[InlineKeyboardButton("Sửa Tên đăng nhập", callback_data='edit_username')],
                    [InlineKeyboardButton("Sửa Mật khẩu", callback_data='edit_password')],
                    [InlineKeyboardButton("Sửa Bí danh", callback_data='edit_user_alias')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Đang sửa user `{user_id}`. Bạn muốn sửa gì?", reply_markup=reply_markup, parse_mode='Markdown')
        return EDITUSER_CHOOSE_FIELD
    except ValueError:
        await update.message.reply_text("ID không hợp lệ.")
        return EDITUSER_ID

async def edituser_choose_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    field_to_edit = query.data.split('_')[1]
    context.user_data['field_to_edit'] = field_to_edit
    await query.edit_message_text(text=f"OK. Nhập giá trị mới cho `{field_to_edit}`:", parse_mode='Markdown')
    return EDITUSER_GET_NEW_VALUE

async def edituser_get_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_value = update.message.text
    user_id = context.user_data['edit_user_id']
    field = context.user_data['field_to_edit']
    
    if field == 'password': await update.message.delete()
    
    ConfigManager().update_user_field(user_id, field, new_value)
    await update.message.reply_text(f"✅ Đã cập nhật `{field}` cho người dùng `{user_id}`.")
    return ConversationHandler.END

# === /deluser: Xóa người dùng ===
async def deluser_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update): return ConversationHandler.END
    await update.message.reply_text("Nhập ID Telegram của người dùng bạn muốn XÓA:")
    return DELUSER_ID

async def deluser_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_id = int(update.message.text)
        if not ConfigManager().user_exists(user_id):
            await update.message.reply_text("❌ Không tìm thấy người dùng.")
            return ConversationHandler.END
        
        context.user_data['delete_user_id'] = user_id
        await update.message.reply_text(f"⚠️ CẢNH BÁO: Bạn sắp xóa người dùng `{user_id}` và tất cả tác vụ của họ. Gõ `yes` để xác nhận.", parse_mode='Markdown')
        return DELUSER_CONFIRM
    except ValueError:
        await update.message.reply_text("ID không hợp lệ.")
        return DELUSER_ID

async def deluser_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() == 'yes':
        user_id = context.user_data['delete_user_id']
        if ConfigManager().delete_user(user_id): await update.message.reply_text(f"✅ Đã xóa thành công người dùng `{user_id}`.")
        else: await update.message.reply_text(f"❌ Lỗi khi xóa người dùng.")
    else:
        await update.message.reply_text("Đã hủy thao tác xóa.")
    return ConversationHandler.END


# --- QUY TRÌNH HỘI THOẠI: QUẢN LÝ TÁC VỤ (ADMIN) ---
# ... (Các hàm cho /addsheet, /editsheet, /delsheet tương tự như /adduser, /edituser, /deluser) ...


# --- HÀM HỦY BỎ CHUNG ---
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Hủy bỏ cuộc hội thoại hiện tại một cách an toàn."""
    await update.message.reply_text("Đã hủy thao tác hiện tại.")
    context.user_data.clear() # Xóa dữ liệu tạm
    return ConversationHandler.END


# --- HÀM SETUP BOT ---
def setup_bot():
    """Thiết lập bot và tất cả các handler."""
    global bot_instance
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    bot_instance = application.bot

    # Handler cho việc lập lịch
    schedule_conv = ConversationHandler(
        entry_points=[CommandHandler("schedule", schedule_start)],
        states={SCHEDULE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_received)]},
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    # Handler cho việc thêm người dùng
    adduser_conv = ConversationHandler(
        entry_points=[CommandHandler("adduser", adduser_start)],
        states={
            ADDUSER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, adduser_get_id)],
            ADDUSER_UNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, adduser_get_username)],
            ADDUSER_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adduser_get_password)],
            ADDUSER_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adduser_get_alias)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )

    # Handler cho việc sửa người dùng
    edituser_conv = ConversationHandler(
        entry_points=[CommandHandler("edituser", edituser_start)],
        states={
            EDITUSER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, edituser_get_id)],
            EDITUSER_CHOOSE_FIELD: [CallbackQueryHandler(edituser_choose_field)],
            EDITUSER_GET_NEW_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edituser_get_new_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )

    # Handler cho việc xóa người dùng
    deluser_conv = ConversationHandler(
        entry_points=[CommandHandler("deluser", deluser_start)],
        states={
            DELUSER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, deluser_get_id)],
            DELUSER_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, deluser_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    
    # Thêm tất cả handler vào application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_now))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("cancel", cancel_schedule))
    
    application.add_handler(schedule_conv)
    application.add_handler(adduser_conv)
    application.add_handler(edituser_conv)
    application.add_handler(deluser_conv)
    # (Thêm các handler cho add/edit/delete sheet tại đây)

    return application
