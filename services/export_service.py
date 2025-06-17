from interfaces.data_source import IDataSource
from interfaces.data_processor import IDataProcessor
from interfaces.data_destination import IDataDestination
from interfaces.post_export_action import IPostExportAction

class ExportService:
    def __init__(self, source: IDataSource, processor: IDataProcessor, destination: IDataDestination, post_action: IPostExportAction = None):
        self._source = source
        self._processor = processor
        self._destination = destination
        self._post_action = post_action

    def run(self) -> str: # Trả về đường dẫn file output
        print("\n🚀 Bắt đầu quy trình xuất dữ liệu...")
        data = self._source.read()
        processed_data = self._processor.process(data)
        output_filepath = self._destination.write(processed_data)
        
        if self._post_action and output_filepath:
            self._post_action.execute(output_filepath)
            
        print("🎉 Quy trình xuất dữ liệu hoàn tất.")
        return output_filepath
