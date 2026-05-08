import json
import os
from typing import List, Dict

class ChunkFolderExporter:
    """
    Exporta cada chunk como un archivo JSON independiente dentro de una carpeta
    Estructura: data/output/{document_id}/{seq:04d}_{article_id}.json
    """
    
    def __init__(self, output_dir="data/output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_document(self, doc_result: Dict) -> Dict:
        """
        Exporta todos los chunks de un documento a archivos individuales
        
        Returns: {
            "folder_path": "data/output/xxx/",
            "chunk_count": 42,
            "files": ["0001_art_1.json", ...]
        }
        """
        doc_id = doc_result["document_id"]
        folder_path = os.path.join(self.output_dir, doc_id)
        os.makedirs(folder_path, exist_ok=True)
        
        exported_files = []
        
        for idx, chunk in enumerate(doc_result["chunks"], start=1):
            # Nombre de archivo: 0001_art_1.json (ordenado y legible)
            article_num = chunk["hierarchy"].get("article_number", str(idx))
            # Limpiar caracteres especiales del número de artículo
            article_clean = article_num.replace("°", "").replace(".", "")
            
            filename = f"{idx:04d}_art_{article_clean}.json"
            filepath = os.path.join(folder_path, filename)
            
            # Construir documento plano para Elastic (sin el array de chunks)
            elastic_doc = {
                "document_id": doc_result["document_id"],
                "title": doc_result["title"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": idx,
                "total_chunks": len(doc_result["chunks"]),
                "hierarchy": chunk["hierarchy"],
                "content": chunk["content"],
                "embedding": chunk["embedding"],
                "metadata": doc_result["metadata"]
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(elastic_doc, f, ensure_ascii=False, indent=2)
            
            exported_files.append(filename)
        
        # archivo de control: metadata de la carpeta
        manifest = {
            "document_id": doc_id,
            "title": doc_result["title"],
            "total_chunks": len(doc_result["chunks"]),
            "exported_at": None,  # podrías poner timestamp
            "files": exported_files
        }
        
        manifest_path = os.path.join(folder_path, "_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"[EXPORT] {len(doc_result['chunks'])} chunks → {folder_path}/")
        
        return {
            "folder_path": folder_path,
            "chunk_count": len(doc_result["chunks"]),
            "manifest": manifest_path,
            "files": exported_files
        }