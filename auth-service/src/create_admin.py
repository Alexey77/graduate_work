import argparse

from core.config import db_settings
from core.logger import get_logger
from models.entity import Permission, Role, User
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

URI = db_settings.URI_FOR_CLI

logger = get_logger(__name__)


def convert_async_uri_to_sync(uri: str) -> str:
    if "aiosqlite" in uri:
        return uri.replace("sqlite+aiosqlite", "sqlite")
    elif "asyncpg" in uri:
        return uri.replace("postgresql+asyncpg", "postgresql")
    elif "aiomysql" in uri:
        return uri.replace("mysql+aiomysql", "mysql")

    return uri


def create_engine_and_session():
    engine = create_engine(convert_async_uri_to_sync(URI))
    session_maker = sessionmaker(bind=engine)
    return engine, session_maker


def create_or_get_role(session, role_name, permission_name):
    # Проверяем, существует ли разрешение
    permission = session.execute(
        select(Permission).where(Permission.name == permission_name)
    ).scalar()
    if not permission:
        permission = Permission(name=permission_name)
        session.add(permission)
        session.commit()

    # Проверяем, существует ли роль
    role = session.execute(select(Role).where(Role.name == role_name)).scalar()
    if not role:
        role = Role(name=role_name, permissions=[permission])
        session.add(role)
        session.commit()

    return role


def add_user(args, session):
    # Проверяем, существует ли уже такой пользователь
    if session.execute(select(User).where(User.login == args.login)).scalar():
        logger.warning(f"User with login {args.login} already exists.")
        return

    # Создаем пользователя
    user = User(
        login=args.login,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name,
    )
    session.add(user)

    # Создаем или получаем роль 'admin' и 'guest'
    admin_role = create_or_get_role(session, "admin", "admin")
    guest_role = create_or_get_role(session, "guest", "guest")
    user_role = create_or_get_role(session, "user", "user")

    # Присваиваем роли 'admin', 'user' и 'guest' пользователю
    user.roles.append(admin_role)
    user.roles.append(guest_role)
    user.roles.append(user_role)
    session.commit()

    logger.info(f"User {args.login} with roles 'admin', 'user' and 'guest' successfully created.")


def main():
    parser = argparse.ArgumentParser(
        description="Добавление администратора в базу данных."
    )
    parser.add_argument("-l", "--login", required=True, help="Логин пользователя")
    parser.add_argument("-p", "--password", required=True, help="Пароль пользователя")
    parser.add_argument("-f", "--first_name", help="Имя пользователя", default="")
    parser.add_argument("-n", "--last_name", help="Фамилия пользователя", default="")

    args = parser.parse_args()

    # Создаем подключение к базе данных и сессию
    engine, session_maker = create_engine_and_session()
    session_maker = session_maker()

    try:
        add_user(args, session_maker)
    except IntegrityError as e:
        logger.error(f"Database error: {e}")
    finally:
        session_maker.close()
        engine.dispose()


if __name__ == "__main__":
    main()
