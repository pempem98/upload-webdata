from abc import ABC, abstractmethod

class IPostExportAction(ABC):
    @abstractmethod
    def execute(self, file_path: str):
        pass
