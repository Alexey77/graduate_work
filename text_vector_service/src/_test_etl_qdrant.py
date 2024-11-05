from itertools import count
from pathlib import Path

import torch
from core.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logger = get_logger(__name__)

# _____________TEST DATA_____________
# https://github.com/JoannaBy/RussianNovels/tree/master
# INPUT_FOLDER = Path("/home/artem/Документы/graduate_work/RussianNovels/corpus")

# _______________PROD DATA_____________
INPUT_FOLDER = None
# ______________Малая моделька_____________
MODEL_NAME = "intfloat/multilingual-e5-small"
VECTOR_SIZE = 384

# ______________Большая моделька_____________
# MODEL_NAME = "intfloat/multilingual-e5-large"
# VECTOR_SIZE = 1024

# ______не в докере_______
QDRANT_HOST = "localhost"

# _______в докере
# QDRANT_HOST = "qdrant"


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "text_fragments"
BATCH_SIZE = 1000
MAX_POINTS = 100

unique_id_counter = count(1)


def create_snapshot(client: QdrantClient, collection_name: str):
    client.create_snapshot(collection_name=collection_name)


def load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name, device='cuda' if torch.cuda.is_available() else 'cpu')


def get_txt_files(folder: Path) -> list[Path]:
    return list(folder.glob("**/*.txt"))


def read_file(file_path: Path) -> str:
    return file_path.read_text(encoding='utf-8')


def split_text(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
                                                   length_function=len)
    return text_splitter.split_text(text)


def encode_texts(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()


def prepare_points(fragments: list[str], vectors: list[list[float]], file_path: Path) -> list[PointStruct]:
    return [
        PointStruct(id=next(unique_id_counter), vector=vector, payload={"source": fragment, "filename": str(file_path)})
        for fragment, vector in zip(fragments, vectors)]


def connect_qdrant(host: str, port: int, collection_name: str) -> QdrantClient:
    client = QdrantClient(host=host, port=port)
    if collection_name not in [c.name for c in client.get_collections().collections]:
        client.create_collection(collection_name=collection_name,
                                 vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE))
    return client


def insert_points(client: QdrantClient, collection_name: str, points: list[PointStruct]):
    client.upsert(collection_name=collection_name, points=points)


def main():
    model = load_model(MODEL_NAME)
    qdrant_client = connect_qdrant(QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME)
    txt_files = get_txt_files(INPUT_FOLDER)

    batch_points = []
    total_points = 0

    for file_path in tqdm(txt_files, desc="Processing files"):
        try:
            text = read_file(file_path)
            fragments = split_text(text)[:MAX_POINTS]
            if fragments:
                vectors = encode_texts(model, fragments)
                points = prepare_points(fragments, vectors, file_path)
                batch_points.extend(points)
                total_points += len(points)

                if len(batch_points) >= BATCH_SIZE:
                    insert_points(qdrant_client, QDRANT_COLLECTION_NAME, batch_points[:BATCH_SIZE])
                    batch_points = []
        except (OSError, ValueError, FileNotFoundError) as e:
            logger.error(f"Error processing file {file_path}: {e}")

    if batch_points:
        insert_points(qdrant_client, QDRANT_COLLECTION_NAME, batch_points[:BATCH_SIZE])

    logger.info(f"Processed a total of {total_points} points.")
    create_snapshot(qdrant_client, QDRANT_COLLECTION_NAME)
    logger.info("ETL process completed successfully.")


if __name__ == "__main__":
    main()
