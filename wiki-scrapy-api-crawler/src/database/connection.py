import sqlite3
from sqlite3 import Error

from loguru import logger

logger.add(f"output/_LOG/{__name__}.log", rotation="10 MB", compression="zip")

class DatabaseConnection:
    """Базовый класс для управления соединением с базой данных"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        logger.info(f"Database initialized with path: {db_path}")

    def connect(self):
        """Открывает соединение с базой данных"""
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_path)
                logger.info("Connection to the database established.")
            except Error as e:
                logger.error(f"Failed to connect to the database: {e}")
                raise

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

    def get_connection(self):
        """Возвращает активное соединение с базой данных"""
        self.connect()
        return self.conn
