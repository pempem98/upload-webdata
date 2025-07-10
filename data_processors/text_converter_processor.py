import pandas as pd
from interfaces import IDataProcessor

class TextConverterProcessor(IDataProcessor):
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        print("✨ Đang chuyển đổi toàn bộ dữ liệu sang định dạng Text...")
        if data.empty:
            print("⚠️ Cảnh báo: Dữ liệu đầu vào rỗng, không có gì để xử lý.")
            return data
        return data.astype(str)
