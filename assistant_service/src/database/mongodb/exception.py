from database.exception import DatabaseException


class MongoDBException(DatabaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
