from src.parsers.html_cleaner import HTMLCleaner
from src.chunkers.hierarchical_chunker import HierarchicalChunker
from src.services.embedding_service import EmbeddingService
from src.exporters.chunk_folder_exporter import ChunkFolderExporter  # ← Cambio


class LegislationPipeline:

    def __init__(self):
        self.embedder = EmbeddingService()
        self.exporter = ChunkFolderExporter()  # ← Usa el nuevo

    def process(self, doc: dict):
        """
        Pipeline principal
        """
        cleaned_text = HTMLCleaner.clean(doc.get("content", ""))
        chunks = HierarchicalChunker.chunk(cleaned_text, doc.get("id"), doc)
        enriched_chunks = self.process_chunks(chunks, doc)

        final_data = {
            "document_id": doc.get("id"),
            "title": doc.get("title"),
            "metadata": self.build_metadata(doc),
            "chunks": enriched_chunks
        }

        # Exportar como carpeta + archivos individuales
        result = self.exporter.export_document(final_data)
        
        return result  # ← Retorna info de exportación

    def process_chunks(self, chunks: list[dict], doc: dict):
        """Agrega embeddings a cada chunk"""
        results = []
        for chunk in chunks:
            enriched = chunk.copy()
            enriched["embedding"] = self.embedder.embed_chunk({
                "content": chunk.get("content", "")
            })["embedding"]
            results.append(enriched)
        return results

    def build_metadata(self, doc: dict):
        """Extrae metadata (igual que antes)"""
        return {
            "publication": doc.get("publication"),
            "jurisdiction": doc.get("jurisdictionDescription"),
            "tags": [tag.get("value") for tag in doc.get("documentTags", [])],
            "law_number": doc.get("issuersLegislationTitle"),
            "sanction_date": doc.get("legislationSanctionDateString"),
            "promulgation_date": doc.get("legislationEnacmentDateString"),
            "online_reference": doc.get("onlineReference")
        }