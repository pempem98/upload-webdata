import pandas as pd
import os
from datetime import datetime
from interfaces.data_destination import IDataDestination

class ExcelDestination(IDataDestination):
    def __init__(self, base_path: str, telegram_id: int, spreadsheet_name: str):
        # Tạo tên file an toàn từ tên sheet
        safe_sheet_name = "".join(c for c in spreadsheet_name if c.isalnum() or c in (' ', '_')).rstrip()
        
        # Tạo đường dẫn động
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self._output_path = os.path.join(base_path, str(telegram_id), current_time)
        self._output_filename = os.path.join(self._output_path, f"{safe_sheet_name}.xlsx")

    def write(self, data: pd.DataFrame) -> str:
        # Tạo các thư mục cha nếu chúng chưa tồn tại
        os.makedirs(self._output_path, exist_ok=True)
        
        print(f"💾 Đang lưu file vào '{self._output_filename}'...")
        data.to_excel(self._output_filename, index=False, engine='openpyxl')
        print(f"✅ Đã lưu thành công!")
        return self._output_filename
    
    def get_dir(self) -> str:
        return self._output_path
