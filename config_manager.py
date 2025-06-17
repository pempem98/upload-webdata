import sqlite3
from typing import List, Dict, Any, Optional, Tuple

class ConfigManager:
    def __init__(self, db_path='app.db'):
        self._db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self._db_path)

    # --- HÀM GHI MỚI, SỬA, XÓA ---
    def add_or_update_user(self, telegram_id: int, web_username: str, web_password: str, user_alias: str = 'user'):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (telegram_id, username, password, user_alias) VALUES (?, ?, ?, ?)",
            (telegram_id, web_username, web_password, user_alias)
        )
        conn.commit()
        conn.close()

    def update_user_field(self, telegram_id: int, field: str, value: str) -> bool:
        """Cập nhật một trường cụ thể (username, password, or user_alias) cho người dùng."""
        if field not in ['username', 'password', 'user_alias']:
            return False # Ngăn chặn SQL injection
        conn = self._get_connection()
        cursor = conn.cursor()
        # Dùng f-string một cách an toàn để chèn tên cột
        cursor.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, telegram_id))
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_rows > 0

    def delete_user(self, telegram_id: int) -> bool:
        """Xóa người dùng và tất cả các sheet liên quan của họ."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Phải xóa các sheet trước do ràng buộc khóa ngoại
        cursor.execute("DELETE FROM sheets WHERE user_id = ?", (telegram_id,))
        # Sau đó mới xóa người dùng
        cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_rows > 0

    def add_sheet_for_user(self, user_id: int, spreadsheet_name: str, worksheet_name: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sheets (user_id, spreadsheet_name, worksheet_name) VALUES (?, ?, ?)",
            (user_id, spreadsheet_name, worksheet_name)
        )
        conn.commit()
        conn.close()

    def update_sheet_field(self, sheet_id: int, field: str, value: str) -> bool:
        """Cập nhật một trường của sheet dựa vào ID của sheet."""
        if field not in ['spreadsheet_name', 'worksheet_name']:
            return False
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE sheets SET {field} = ? WHERE id = ?", (value, sheet_id))
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_rows > 0

    def delete_sheet(self, sheet_id: int) -> bool:
        """Xóa một sheet cụ thể bằng ID của nó."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sheets WHERE id = ?", (sheet_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_rows > 0
        
    # --- CÁC HÀM ĐỌC DỮ LIỆU ---
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Lấy thông tin của một người dùng."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user_credentials(self, telegram_id: int) -> Optional[Tuple[str, str]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE telegram_id = ?", (telegram_id,))
        credentials = cursor.fetchone()
        conn.close()
        return credentials

    def get_user_sheets(self, telegram_id: int) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sheets WHERE user_id = ?", (telegram_id,))
        sheets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sheets

    def user_exists(self, telegram_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
