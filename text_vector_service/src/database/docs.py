import logging
from qdrant_client import models

from . import BaseQdrantClient

logger = logging.getLogger(__name__)


class VectorDocument(BaseQdrantClient):
    def __init__(
            self,
            host: str,
            port: int,
            collection_name: str,
            vector_size: int = 1024
    ) -> None:
        """
        Инициализация коллекции документов.

        Args:
            host: Хост Qdrant
            port: Порт Qdrant
            collection_name: Имя коллекции
            vector_size: Размерность вектора (по умолчанию 1024)
        """
        super().__init__()
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.host = host
        self.port = port

    async def initialize(self) -> None:
        """Инициализация клиента и создание коллекции."""
        await self.init_client(self.host, self.port)
        await self._create_collection(
            self.collection_name,
            self.vector_size
        )

    async def add_document(
            self,
            vector: list[float],
            metadata: dict[str, str],
            document_id: str
    ) -> bool:
        """
        Добавление документа в коллекцию.

        Args:
            vector: Векторное представление документа
            metadata: Метаданные документа
            document_id: UUID документа
        """
        point = models.PointStruct(
            id=document_id,
            vector=vector,
            payload=metadata
        )
        return await self._upsert_points(self.collection_name, [point])

    async def delete_document(self, document_id: str) -> bool:
        """Удаление документа по ID."""
        return await self._delete_points(self.collection_name, [document_id])

    async def search_similar(
            self,
            query_vector: list[float],
            limit: int = 5
    ) -> list[dict]:
        """
        Поиск похожих документов.

        Args:
            query_vector: Векторное представление запроса
            limit: Количество результатов

        Returns:
            List[Dict]: Список найденных документов с их метаданными и score
        """
        results = await self._search_points(
            self.collection_name,
            query_vector,
            limit
        )

        return [
            {
                "id": str(point.id),
                "metadata": point.payload,
                "score": point.score
            }
            for point in results
        ]

    async def cleanup(self) -> None:
        """Закрытие соединения."""
        await self.close_client()
