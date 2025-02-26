"""TODO"""
import time
import datetime as dt
from typing import List
from uuid import UUID, uuid4
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)
from sqlalchemy import (
    String, DateTime, Uuid, Integer, ForeignKey, create_engine, select, Table, Column
)
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin, OAuth2AuthorizationCodeMixin, OAuth2TokenMixin
)


class Base(DeclarativeBase):
    """TODO"""

    type_annotation_map = {
        str: String,
        int: Integer,
        dt.datetime: DateTime 
    }

class User(Base):
    """TODO"""

    __tablename__ = "user"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[int] = mapped_column(default=int(time.time()))
    personal_info: Mapped['PersonalInformation'] = relationship(
        back_populates= 'user', cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username= {self.username})"
    
class PersonalInformation(Base):
    """TODO"""

    __tablename__ = "personal_information"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    telephone_num: Mapped[str] = mapped_column(nullable=True)
    birthday: Mapped[dt.datetime] = mapped_column(nullable=True)
    nationality: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(
        back_populates= 'personal_info'
    )
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'first_name': self.first_name,
            'email': self.email,
            'telephone_num': self.telephone_num,
            'birthday': self.nationality,
            'address': self.address
        }
    
    def __repr__(self) -> str:
        return f"PersonalInformation(id={self.id}, name={self.name}, first_name={self.first_name})"

class Client(Base, OAuth2ClientMixin):
    """TODO"""

    __tablename__ = "client"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_type: Mapped[str] = mapped_column(nullable=True)    
    
    def __repr__(self) -> str:
        return f"Client(id={self.id}, client_id={self.client_id})"
    
class AuthorizationCode(Base, OAuth2AuthorizationCodeMixin):
    """TODO"""

    __tablename__ = "authorization_code"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship()
    
    def __repr__(self) -> str:
        return f"AuthorizationCode(id={self.id}, client_id={self.client_id})"
    
class Token(Base, OAuth2TokenMixin):
    """TODO"""

    __tablename__ = "token"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship()
    
    def is_refresh_token_active(self):
        if self.is_revoked():
            return False
        expires_at = self.issued_at + self.expires_in 
        return expires_at >= time.time()





    
    