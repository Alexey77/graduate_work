from typing import Any

from loguru import logger

from .repository import SQLiteRepository

logger.add(f"output/_LOG/{__name__}.log", rotation="10 MB", compression="zip")


class WikiPageRepository(SQLiteRepository):
    """Репозиторий для работы с wiki страницами"""

    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = "wiki_page"

    def create_database(self):
        """Создание таблицы wiki_page"""
        query = """
        CREATE TABLE IF NOT EXISTS wiki_page (
            page_id INTEGER PRIMARY KEY,
            title TEXT,
            wikitext TEXT,
            url TEXT,
            source TEXT,
            lang TEXT,
            revision_id INTEGER,
            created_at TEXT,
            updated_at TEXT,
            time_request TEXT
        )
        """
        self.execute_query(query)
        logger.info("Wiki page table created successfully")

    def insert_or_update_item(self, item_data: dict[str, Any]):
        """Вставка или обновление wiki страницы"""
        if self._item_exists(item_data["page_id"]):
            if self._is_revision_same(item_data):
                self._update_time_request(item_data)
            else:
                self._update_item_fields(item_data)
        else:
            self.create(self.table_name, item_data)

    def _item_exists(self, page_id: int) -> bool:
        """Проверяет существование страницы"""
        result = self.read(self.table_name, {"page_id": page_id})
        return len(result) > 0

    def _is_revision_same(self, item_data: dict[str, Any]) -> bool:
        """Проверяет идентичность ревизии"""
        query = "SELECT revision_id FROM wiki_page WHERE page_id = ?"
        result = self.execute_query(query, (item_data["page_id"],))
        return result and result[0][0] == item_data["revision_id"]

    def _update_time_request(self, item_data: dict[str, Any]):
        """Обновляет время запроса"""
        self.update(
            self.table_name,
            {"time_request": item_data["time_request"]},
            {"page_id": item_data["page_id"]}
        )

    def _update_item_fields(self, item_data: dict[str, Any]):
        """Обновляет все поля страницы"""
        update_data = {k: v for k, v in item_data.items() if k != "created_at"}
        self.update(
            self.table_name,
            update_data,
            {"page_id": item_data["page_id"]}
        )
