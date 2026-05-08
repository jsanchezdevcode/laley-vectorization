from sentence_transformers import SentenceTransformer
from typing import List
from .base import EmbeddingProvider

class SentenceTransformersProvider(EmbeddingProvider):

    def __init__(self, model_name: str = "intfloat/multilingual-e5-base"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()