import sqlite3

def setup_database():
    """
    Tạo/cập nhật database.
    - Bảng 'users' sẽ có thêm username và password.
    - Bảng 'sheets' sẽ đổi tên cột và không còn username/password.
    - Nạp dữ liệu ban đầu từ file config cũ.
    """
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    print("Tạo bảng 'users' với username và password...")
    # Thêm cột username và password vào bảng users
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
    except sqlite3.OperationalError:
        print("Các cột username/password đã tồn tại trong bảng users.")
        
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        user_alias TEXT
    )
    ''')

    print("Tạo bảng 'sheets' với spreadsheet_name...")
    # Đổi tên cột google_sheet_name và xóa username/password
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sheets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        spreadsheet_name TEXT NOT NULL,
        worksheet_name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
    )
    ''')
    
    # === NẠP DỮ LIỆU BAN ĐẦU TỪ CONFIG CŨ CỦA BẠN ===
    admin_user_id = 5749118184
    admin_username = 'lethuhien@gmail.com'
    admin_password = '123456'
    
    spreadsheet_name_from_config = 'UP WEB TỔNG MGA, MLS, MTS, LSB'
    worksheet_name_from_config = 'Căn hộ cao tầng'
    
    try:
        print("Cập nhật thông tin đăng nhập cho người dùng admin...")
        cursor.execute(
            "INSERT OR REPLACE INTO users (telegram_id, username, password, user_alias) VALUES (?, ?, ?, ?)",
            (admin_user_id, admin_username, admin_password, 'admin')
        )

        print("Thêm tác vụ sheet ban đầu...")
        cursor.execute(
            """
            INSERT OR IGNORE INTO sheets (user_id, spreadsheet_name, worksheet_name) 
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM sheets WHERE user_id = ? AND spreadsheet_name = ?
            )
            """,
            (admin_user_id, spreadsheet_name_from_config, worksheet_name_from_config,
             admin_user_id, spreadsheet_name_from_config)
        )
    except Exception as e:
        print(f"Lỗi khi nạp dữ liệu ban đầu: {e}")

    conn.commit()
    conn.close()
    print("✅ Database đã được cập nhật thành công.")

if __name__ == '__main__':
    setup_database()