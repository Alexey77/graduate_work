from pathlib import Path

import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# https://github.com/JoannaBy/RussianNovels/tree/master

# ===========================
# Configuration Variables
# ===========================

# Input folder containing text files
INPUT_FOLDER = Path("/path/to/input/folder")  # Замените на ваш путь

# Text splitter configuration
CHUNK_SIZE = 1000  # Настройте по необходимости
CHUNK_OVERLAP = 100  # Настройте по необходимости

# SentenceTransformer model configuration
MODEL_NAME = "intfloat/multilingual-e5-large"
VECTOR_SIZE = 1024

# Qdrant configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "text_fragments"

# Batch size for Qdrant insertion
BATCH_SIZE = 100


# ===========================
# Function Definitions
# ===========================

def load_model(model_name: str) -> SentenceTransformer:
    """
    Load the SentenceTransformer model.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model '{model_name}' on {device}...")  # noqa T201
    model = SentenceTransformer(model_name, device=device)
    print("Model loaded successfully.")  # noqa T201
    return model


def get_txt_files(folder: Path) -> list[Path]:
    """
    Retrieve all .txt files from the specified folder.
    """
    return list(folder.glob("**/*.txt"))


def read_file(file_path: Path) -> str:
    """
    Read the content of a text file.
    """
    return file_path.read_text(encoding='utf-8')


def split_text(text: str) -> list[str]:
    """
    Split text into smaller fragments using RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False
    )
    return text_splitter.split_text(text)


def encode_texts(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """
    Encode a list of texts into vector representations.
    """
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()


def prepare_points(fragments: list[str], vectors: list[list[float]], file_path: Path) -> list[PointStruct]:
    """
    Prepare Qdrant PointStruct objects with payload.
    """
    points = []
    for fragment, vector in zip(fragments, vectors):
        payload = {
            "source": fragment,
            "filename": str(file_path)
        }
        point = PointStruct(
            vector=vector,
            payload=payload
        )
        points.append(point)
    return points


def connect_qdrant(host: str, port: int, collection_name: str) -> QdrantClient:
    """
    Connect to Qdrant and create collection if it doesn't exist.
    """
    client = QdrantClient(host=host, port=port)

    # Проверка существования коллекции
    existing_collections = client.get_collections().collections
    collection_names = [c.name for c in existing_collections]

    if collection_name not in collection_names:
        print(f"Создание коллекции '{collection_name}'...")  # noqa T201
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"Коллекция '{collection_name}' создана.")  # noqa T201
    else:
        print(f"Коллекция '{collection_name}' уже существует.")  # noqa T201

    return client


def insert_points(client: QdrantClient, collection_name: str, points: list[PointStruct]):
    """
    Insert points into Qdrant collection.
    """
    client.upsert(
        collection_name=collection_name,
        points=points
    )


# ===========================
# Main ETL Process
# ===========================

def main():
    # Загрузка модели
    model = load_model(MODEL_NAME)

    # Подключение к Qdrant
    qdrant_client = connect_qdrant(QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME)

    # Получение списка txt файлов
    txt_files = get_txt_files(INPUT_FOLDER)
    print(f"Найдено {len(txt_files)} текстовых файлов для обработки.")  # noqa T201

    # Инициализация списка для пакетной вставки
    batch_points = []

    # Итерация по каждому текстовому файлу с отображением прогресса
    for file_path in tqdm(txt_files, desc="Обработка файлов"):
        try:
            # Чтение содержимого файла
            text = read_file(file_path)

            # Разбиение текста на фрагменты
            fragments = split_text(text)

            if not fragments:
                continue

            # Векторизация фрагментов
            vectors = encode_texts(model, fragments)

            # Подготовка точек для Qdrant
            points = prepare_points(fragments, vectors, file_path)

            # Добавление точек в батч
            batch_points.extend(points)

            # Вставка в Qdrant при достижении размера батча
            if len(batch_points) >= BATCH_SIZE:
                insert_points(qdrant_client, QDRANT_COLLECTION_NAME, batch_points)
                batch_points = []

        except Exception as e:  # noqa BLE001
            print(f"Ошибка при обработке файла {file_path}: {e}")  # noqa T201

    # Вставка оставшихся точек
    if batch_points:
        insert_points(qdrant_client, QDRANT_COLLECTION_NAME, batch_points)

    print("ETL процесс завершен успешно.")  # noqa T201


if __name__ == "__main__":
    main()
