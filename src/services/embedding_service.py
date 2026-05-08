from src.embeddings.factory import get_embedding_provider

class EmbeddingService:

    def __init__(self):
        self.provider = get_embedding_provider()

    def embed_chunk(self, chunk: dict) -> dict:
        text = chunk["content"]
        vector = self.provider.embed(text)

        chunk["embedding"] = vector
        return chunk