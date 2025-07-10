import gspread
import pandas as pd
from interfaces import IDataSource

class GSpreadClient:
    _instance = None
    @classmethod
    def get_instance(cls, service_account_file: str):
        if cls._instance is None:
            print("🔄 Khởi tạo GSpread Client (Singleton)...")
            cls._instance = gspread.service_account(filename=service_account_file)
        return cls._instance

class GoogleSheetSource(IDataSource):
    def __init__(self, service_account_file: str, sheet_name: str, worksheet_name: str):
        self._client = GSpreadClient.get_instance(service_account_file)
        self._sheet_name = sheet_name
        self._worksheet_name = worksheet_name

    def read(self) -> pd.DataFrame:
        try:
            print(f"📄 Đang mở Google Sheet: '{self._sheet_name}'...")
            spreadsheet = self._client.open(self._sheet_name)
            print(f"📑 Đang chọn trang tính: '{self._worksheet_name}'...")
            worksheet = spreadsheet.worksheet(self._worksheet_name)
            print("📥 Đang tải dữ liệu...")
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ Lỗi: Không tìm thấy Google Sheet với tên '{self._sheet_name}'.")
            raise
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ Lỗi: Không tìm thấy trang tính '{self._worksheet_name}'.")
            raise
