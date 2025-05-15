from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'auth_user'
    id = Column(Integer, primary_key=True)


class Tag(Base):
    __tablename__ = 'app_quote_tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('auth_user.id', ondelete='SET NULL', onupdate='CASCADE'))


class Author(Base):
    __tablename__ = 'app_quote_author'
    id = Column(Integer, primary_key=True)
    fullname = Column(String(150), nullable=False)
    created = Column(DateTime, nullable=False)
    born_date = Column(DateTime, nullable=False)
    born_location = Column(String(100), nullable=False)
    description = Column(String(10000), nullable=True)
    user_id = Column(Integer, ForeignKey('auth_user.id', ondelete='SET NULL', onupdate='CASCADE'))
    # quotes = relationship('Quote', back_populates='app_quote_author')


class Quote(Base):
    __tablename__ = 'app_quote_quote'
    id = Column(Integer, primary_key=True)
    quote = Column(String(2500), nullable=False)
    created = Column(DateTime, nullable=False, server_default='now()')
    author_id = Column(Integer, ForeignKey('app_quote_author.id', ondelete='SET NULL', onupdate='CASCADE'))
    user_id = Column(Integer, ForeignKey('auth_user.id', ondelete='SET NULL', onupdate='CASCADE'))

    # author_id = relationship('Author', back_populates='app_quote_quote')
    # tags = relationship('Tag', secondary='app_quote_quote_tags', back_populates='app_quote_quote')


class QuoteToTag(Base):
    __tablename__ = 'app_quote_quote_tags'
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('app_quote_quote.id', ondelete='CASCADE', onupdate='CASCADE'))
    tag_id = Column(Integer, ForeignKey('app_quote_tag.id', ondelete='CASCADE', onupdate='CASCADE'))

    # quote_id = relationship('Quote', back_populates='app_quote_quote_tags')
    # subject_id = relationship('Subject', back_populates='app_quote_quote_tags')
