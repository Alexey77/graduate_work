import time

from core.config import encoder_settings, vector_db_settings
from core.logger import get_logger
from model_manager import ModelManager
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
from text_splitter import TextSplitter

from etl_wiki.db_iterator import SQLiteIterator

logger = get_logger(__name__)

BATCH_SIZE = 1000

SQLITE_PATH = 'E:\\temp\\wiki\\wiki_pages.sqlite'


def get_vector_from_texts(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()


def main():
    logger.info("Initializing Qdrant client.")
    client = QdrantClient(host=vector_db_settings.HOST,
                          port=vector_db_settings.PORT)

    db_path = SQLITE_PATH
    # max_docs = 120
    max_docs = None

    logger.info("Setting up model manager and loading model.")
    model_manager = ModelManager(settings=encoder_settings)
    model = model_manager.get_model()

    logger.info("Configuring text splitter.")
    text_splitter = TextSplitter(
        model=model,
        chunk_size=encoder_settings.MAX_LENGTH,
        overlap_percentage=15
    )

    logger.info("Initializing SQLite iterator for wiki pages.")
    wiki_pages = SQLiteIterator(db_path, max_documents=max_docs)

    if not client.collection_exists(collection_name=vector_db_settings.COLLECTION_NAME):
        logger.info("Collection does not exist in Qdrant, creating new collection.")
        vector_size = model.get_sentence_embedding_dimension()
        client.create_collection(
            collection_name=vector_db_settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    else:
        logger.info("Collection already exists in Qdrant.")

    points_buffer = []
    point_id = 0

    for i, doc in enumerate(wiki_pages):
        logger.info(f"Processing wiki page {i}: ID {doc.page_id}, Title '{doc.title}'")

        title = f"Заголовок страницы: {doc.title}. Начало фрагмента:"
        chunks = text_splitter.split_text(title=title, text=doc.text)
        # logger.info(f"Text split into {len(chunks)} chunks.")

        vectors = get_vector_from_texts(model=model, texts=chunks)
        for chunk, vector in zip(chunks, vectors):
            payload = {
                "text": chunk,
                "page_id": doc.page_id,
                "title": doc.title,
                "time_request": doc.time_request.isoformat() if doc.time_request else None
            }

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            points_buffer.append(point)
            point_id += 1

            if len(points_buffer) >= BATCH_SIZE:
                # logger.info(f"Upserting {len(points_buffer)} points to Qdrant.")
                client.upsert(
                    collection_name=vector_db_settings.COLLECTION_NAME,
                    points=points_buffer
                )
                # logger.info(f"Inserted {len(points_buffer)} points into Qdrant.")
                points_buffer = []

    if points_buffer:
        logger.info(f"Final upsert of remaining {len(points_buffer)} points to Qdrant.")
        client.upsert(
            collection_name=vector_db_settings.COLLECTION_NAME,
            points=points_buffer
        )
        logger.info(f"Inserted remaining {len(points_buffer)} points into Qdrant.")


if __name__ == '__main__':
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")
