from enum import Enum


class CacheStorageEnum(str, Enum):
    REDIS = "Redis"
    # MEMCACHED = "Memcached"  # NotImplementedError


class DBStorageEnum(str, Enum):
    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"
