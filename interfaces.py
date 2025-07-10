from abc import ABC, abstractmethod
import pandas as pd

class IDataSource(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame:
        pass

class IDataProcessor(ABC):
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

class IDataDestination(ABC):
    @abstractmethod
    def write(self, data: pd.DataFrame) -> str:
        pass

class IPostExportAction(ABC):
    @abstractmethod
    def execute(self, file_path: str):
        pass
