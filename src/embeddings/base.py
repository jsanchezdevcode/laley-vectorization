from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass