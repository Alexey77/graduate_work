import sqlite3
from collections.abc import Iterator
from datetime import datetime

from .model import WikiPage


class SQLiteIterator:
    def __init__(self, db_path: str, max_documents:int | None = None):
        """
        Инициализирует итератор.

        :param db_path: Путь к SQLite базе данных.
        :param max_documents: Максимальное количество документов для возврата. Если None, возвращаются все документы.
        """
        self.db_path = db_path
        self.max_documents = max_documents

    def __iter__(self) -> Iterator[WikiPage]:
        """
        Возвращает итератор по документам.

        :return: Итератор, возвращающий объекты WikiPage.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT page_id, title, wikitext, url, source, lang, revision_id, created_at, updated_at, time_request FROM wiki_page"

        if self.max_documents is not None:
            query += f" LIMIT {self.max_documents}"

        cursor.execute(query)

        for row in cursor:
            try:
                created_at = datetime.fromisoformat(row[7])
            except ValueError:
                created_at = None

            try:
                updated_at = datetime.fromisoformat(row[8])
            except ValueError:
                updated_at = None

            try:
                time_request = datetime.fromisoformat(row[9])
            except ValueError:
                time_request = None

            document = WikiPage(
                page_id=row[0],
                title=row[1],
                wikitext=row[2],
                url=row[3],
                source=row[4],
                lang=row[5],
                revision_id=row[6],
                created_at=created_at,
                updated_at=updated_at,
                time_request=time_request
            )
            yield document

        conn.close()
