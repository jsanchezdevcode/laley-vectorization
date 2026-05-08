import os
from .sentence_transformers_provider import SentenceTransformersProvider
from .vllm_provider import VLLMEmbeddingProvider

def get_embedding_provider():

    backend = os.getenv("EMBEDDING_BACKEND", "local")

    if backend == "vllm":
        return VLLMEmbeddingProvider(
            endpoint=os.getenv("VLLM_EMBEDDING_URL")
        )

    return SentenceTransformersProvider()