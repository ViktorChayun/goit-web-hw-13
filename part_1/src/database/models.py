from sqlalchemy import Column, Integer, String, Date, Text, func
from sqlalchemy.sql.sqltypes import DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey


Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column("id", Integer, primary_key=True)
    first_name = Column("first_name", String(50), nullable=False)
    last_name = Column("last_name", String(50), nullable=False)
    email = Column("email", String(100), nullable=False, unique=True)
    phone_number = Column("phone_number", String(20), nullable=False)
    birthday = Column("birthday", Date, nullable=False)
    additional_info = Column(Text)  # необов'язкове поле
    created_at = Column('created_at', DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="tags")

    def __repr__(self):
        return f"<Contact(name={self.first_name} {self.last_name}, "\
                "email={self.email}, phone={self.phone_number}, "\
                "birthday={self.birthday})>"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, nullable=False, default=False)
