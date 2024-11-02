import uuid
from datetime import datetime

from models.user_provider import Provider
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(BaseModel):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)

    sessions = relationship('UserSessions',
                            back_populates='user',
                            cascade='all, delete',
                            foreign_keys='UserSessions.user_id')
    roles = relationship('Role', secondary='user_roles', back_populates='users')

    provider_accounts = relationship('ProviderAccount',
                                     back_populates='user',
                                     cascade='all, delete',
                                     foreign_keys='ProviderAccount.user_id')

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = self.hash_password(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    def __repr__(self) -> str:
        return f'<User: {self.login}>'


class UserSessions(BaseModel):
    __tablename__ = 'user_sessions'
    __table_args__ = (
        {'postgresql_partition_by': 'RANGE (created_at)'},
    )

    refresh_token = Column(String(), unique=True, index=True, nullable=False)
    user_agent = Column(String(4096))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)

    user = relationship('User', back_populates='sessions')


class Role(BaseModel):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(1024), nullable=True)

    users = relationship('User', secondary='user_roles', back_populates='roles')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')

    def __repr__(self) -> str:
        return f'<Role: {self.id} ({self.name})>'


class Permission(BaseModel):
    __tablename__ = 'permissions'

    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(1024), nullable=True)

    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')

    def __repr__(self) -> str:
        return f'<Permission: {self.id} ({self.name})>'


class UserRole(BaseModel):
    __tablename__ = 'user_roles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)


class RolePermission(BaseModel):
    __tablename__ = 'role_permissions'

    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)


class ProviderAccount(BaseModel):
    __tablename__ = 'provider_accounts'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    id_social = Column(String(255), nullable=False, unique=True, index=True)
    provider_name = Column(SQLAEnum(Provider), nullable=False)

    user = relationship('User', back_populates='provider_accounts')
