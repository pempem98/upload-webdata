from abc import ABC, abstractmethod
import pandas as pd

class IDataSource(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame:
        pass
