import asyncpg
import pytest_asyncio
from functional.settings import db_setting


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    conn = await asyncpg.connect(dsn=db_setting.db_uri_for_tests)
    yield conn
    await conn.close()
