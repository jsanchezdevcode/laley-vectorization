import requests
from typing import List
from .base import EmbeddingProvider

class VLLMEmbeddingProvider(EmbeddingProvider):

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def embed(self, text: str) -> List[float]:
        response = requests.post(
            self.endpoint,
            json={"input": text}
        )

        return response.json()["embedding"]