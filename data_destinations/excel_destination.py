import pandas as pd
from interfaces.data_destination import IDataDestination

class ExcelDestination(IDataDestination):
    def __init__(self, output_filename: str):
        self._output_filename = output_filename

    def write(self, data: pd.DataFrame) -> str:
        print(f"💾 Đang lưu file vào '{self._output_filename}'...")
        data.to_excel(self._output_filename, index=False, engine='openpyxl')
        print(f"✅ Đã lưu thành công!")
        return self._output_filename
