from sqlite3 import Error
from typing import Any

from loguru import logger


class SQLiteRepository:
    """Базовый репозиторий для выполнения CRUD операций"""

    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query: str, params: tuple = None) -> Any | None:
        """Выполняет SQL запрос и возвращает результат"""
        conn = self.connection.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return None
        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise

    def create(self, table: str, data: dict[str, Any]) -> None:
        """Создает новую запись в таблице"""
        placeholders = ", ".join("?" * len(data))
        columns = ", ".join(data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))
        logger.info(f"Record created in table '{table}': {data}")

    def read(self, table: str, conditions: dict[str, Any] = None) -> list[tuple]:
        """Читает записи из таблицы"""
        query = f"SELECT * FROM {table}"
        params = None

        if conditions:
            where_clause = " AND ".join(f"{key} = ?" for key in conditions)
            query += f" WHERE {where_clause}"
            params = tuple(conditions.values())

        result = self.execute_query(query, params)
        logger.info(f"Records retrieved from table '{table}'")
        return result

    def update(self, table: str, data: dict[str, Any], conditions: dict[str, Any]) -> None:
        """Обновляет записи в таблице"""
        set_clause = ", ".join(f"{key} = ?" for key in data)
        where_clause = " AND ".join(f"{key} = ?" for key in conditions)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(conditions.values())

        self.execute_query(query, params)
        logger.info(f"Record updated in table '{table}': {data} with conditions {conditions}")

    def delete(self, table: str, conditions: dict[str, Any]) -> None:
        """Удаляет записи из таблицы"""
        where_clause = " AND ".join(f"{key} = ?" for key in conditions)
        query = f"DELETE FROM {table} WHERE {where_clause}"

        self.execute_query(query, tuple(conditions.values()))
        logger.info(f"Record deleted from table '{table}' with conditions {conditions}")
