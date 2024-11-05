from logging.config import fileConfig

from alembic import context
from core.config import db_settings
from models.entity import Base
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def convert_async_uri_to_sync(async_uri):
    parts = async_uri.split("+")
    if len(parts) == 2:
        driver, uri = parts
        if driver == "sqlite":
            return f"sqlite:///{uri.split(':///')[-1]}"
        elif driver == "postgresql":
            return uri.replace("postgresql+asyncpg", "postgresql")
        elif driver == "mysql":
            return uri.replace("mysql+aiomysql", "mysql")
    return async_uri


config.set_main_option("sqlalchemy.url", db_settings.URI_FOR_ALEMBIC)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
