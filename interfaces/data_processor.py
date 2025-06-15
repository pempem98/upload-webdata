from abc import ABC, abstractmethod
import pandas as pd

class IDataProcessor(ABC):
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
