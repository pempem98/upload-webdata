from abc import ABC, abstractmethod
import pandas as pd

class IDataDestination(ABC):
    @abstractmethod
    def write(self, data: pd.DataFrame) -> str:
        pass
