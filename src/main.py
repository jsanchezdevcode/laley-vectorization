import os
import json

from src.pipelines.legislation_pipeline import LegislationPipeline
from src.exporters.json_exporter import JSONExporter
from src.repository.document_repository import DocumentRepository

OUTPUT_DIR = "data/output"
INPUT_DIR = "data/input"


def main():

    repo = DocumentRepository("data/laley.sqlite")
    pipeline = LegislationPipeline()
    exporter = JSONExporter(output_dir=OUTPUT_DIR)

    doc_ids = repo.get_all_document_ids()

    for doc_id in doc_ids:

        output_path = os.path.join(OUTPUT_DIR, f"{doc_id}.json")
        input_path = os.path.join(INPUT_DIR, f"{doc_id}.json")

        # 1. ya procesado
        if os.path.exists(output_path):
            print(f"[SKIP OUTPUT] {doc_id}")
            continue

        # 2. no existe input
        if not os.path.exists(input_path):
            print(f"[MISSING INPUT] {doc_id} no existe en input/")
            continue

        # 3. cargar input
        with open(input_path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        # 4. procesar
        print(f"[PROCESS] {doc_id}")
        result = pipeline.process(doc)

        exporter.export(result, doc_id)

        print(f"[DONE] {doc_id}")


if __name__ == "__main__":
    main()