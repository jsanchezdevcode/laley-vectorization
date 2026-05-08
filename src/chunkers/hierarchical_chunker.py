import re
from typing import List, Dict, Optional

class HierarchicalChunker:
    """
    Preserva la jerarquía completa del documento:
    Ley → Libro → Título → Capítulo → Sección → Artículo
    """
    
    # Patrones jerárquicos (ordenados de mayor a menor)
    PATTERNS = {
        'book': re.compile(r'^LIBRO\s+([IVX]+)\s*-?\s*(.*?)$', re.MULTILINE | re.IGNORECASE),
        'title': re.compile(r'^TITULO\s+([^\\n]+?)(?:\s*-?\s*(.*?))?$', re.MULTILINE | re.IGNORECASE),
        'chapter': re.compile(r'^CAPITULO\s+([^\\n]+?)(?:\s*-?\s*(.*?))?$', re.MULTILINE | re.IGNORECASE),
        'section': re.compile(r'^SECCION\s+([^\\n]+?)(?:\s*-?\s*(.*?))?$', re.MULTILINE | re.IGNORECASE),
    }
    
    # Patrón para artículo (captura número + contenido hasta próximo artículo o fin)
    ARTICLE_PATTERN = re.compile(
        r'^Art\.?\s*(\d+°?\.?)\s*-?\.?\s*(.+?)(?=^Art\.|^LIBRO|^TITULO|^CAPITULO|^SECCION|\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    
    @classmethod
    def chunk(cls, text: str, doc_id: str, doc_metadata: Dict) -> List[Dict]:
        """
        Parsea el texto respetando jerarquía y retorna chunks por artículo
        """
        if not text:
            return []
        
        # 1. Extraer estructura jerárquica del documento
        structure = cls._extract_structure(text)
        
        # 2. Extraer todos los artículos con su contexto jerárquico
        chunks = []
        
        for i, article_match in enumerate(cls.ARTICLE_PATTERN.finditer(text)):
            article_num = article_match.group(1).strip()
            article_content = article_match.group(2).strip()
            
            # Encontrar en qué jerarquía está este artículo
            hierarchy = cls._find_hierarchy_for_position(
                article_match.start(), 
                structure
            )
            
            chunk_id = cls._build_chunk_id(doc_id, hierarchy, article_num, i)
            
            chunks.append({
                "chunk_id": chunk_id,
                "hierarchy": {
                    "law_number": doc_metadata.get("issuersLegislationTitle"),
                    "book": hierarchy.get("book"),
                    "title": hierarchy.get("title"),
                    "chapter": hierarchy.get("chapter"),
                    "section": hierarchy.get("section"),
                    "article": f"Artículo {article_num}",
                    "article_number": article_num,
                },
                "content": article_content,
                "embedding": None  # Se llenará después en el pipeline
            })
        
        return chunks
    
    @classmethod
    def _extract_structure(cls, text: str) -> List[Dict]:
        """
        Extrae todas las secciones jerárquicas con sus posiciones
        """
        structure = []
        
        for level, pattern in cls.PATTERNS.items():
            for match in pattern.finditer(text):
                structure.append({
                    "level": level,
                    "value": match.group(1).strip(),
                    "description": match.group(2).strip() if match.lastindex >= 2 else None,
                    "start": match.start(),
                    "end": match.end(),
                    "full_text": match.group(0).strip()
                })
        
        # Ordenar por posición de inicio
        structure.sort(key=lambda x: x["start"])
        return structure
    
    @classmethod
    def _find_hierarchy_for_position(cls, position: int, structure: List[Dict]) -> Dict:
        """
        Dada una posición, encuentra qué jerarquía la contiene
        """
        hierarchy = {
            "book": None,
            "title": None,
            "chapter": None,
            "section": None
        }
        
        for item in structure:
            if item["start"] <= position <= item["end"]:
                hierarchy[item["level"]] = item["value"]
                if item.get("description"):
                    hierarchy[f"{item['level']}_desc"] = item["description"]
        
        return hierarchy
    
    @classmethod
    def _build_chunk_id(cls, doc_id: str, hierarchy: Dict, article_num: str, index: int) -> str:
        """
        Construye un chunk_id significativo: doc-libro-titulo-cap-art
        """
        parts = [doc_id]
        
        if hierarchy.get("book"):
            parts.append(f"lib{hierarchy['book'].lower()}")
        if hierarchy.get("title"):
            # Limpiar título para ID
            title_clean = re.sub(r'[^a-z0-9]', '_', hierarchy['title'].lower())[:20]
            parts.append(f"tit_{title_clean}")
        if hierarchy.get("chapter"):
            chapter_clean = re.sub(r'[^a-z0-9]', '_', hierarchy['chapter'].lower())[:15]
            parts.append(f"cap_{chapter_clean}")
        
        parts.append(f"art{article_num.replace('°', '')}")
        
        return "-".join(parts)