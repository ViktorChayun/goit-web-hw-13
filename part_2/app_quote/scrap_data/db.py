from pathlib import Path
import json
import psycopg2
import sys
from datetime import datetime

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker

from .db_model import Author, Quote, QuoteToTag, Tag

# Додаємо шлях до кореневої папки quotes
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
# from quotes.settings import DATABASES
from configuration.settings import settings, DB_URI

USER = settings.db_user
PASS = settings.db_pass
DB = settings.db_name
HOST = settings.db_host
PORT = settings.db_port
# URI = f"postgresql://{USER}:{DATABASES['default']['PASSWORD']}@{HOST}:{PORT}/{DB}"

engine = create_engine(DB_URI, echo=True, pool_size=5, max_overflow=0)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def insert_data(authors_data, quotes_data):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB,
        user=USER,
        password=PASS,
        host=HOST,
        port=PORT
    )

    cursor = conn.cursor()
    # Insert authors into the database
    for author in authors_data:
        cursor.execute(
            "INSERT INTO app_quote_author (fullname, born_date, born_location, description) VALUES (%s, %s, %s, %s)",
            (author['fullname'], author['born_date'], author['born_location'], author['description'])
        )

    # Insert quotes into the database
    for quote in quotes_data:
        cursor.execute(
            "INSERT INTO app_quote_quote (quote, author, tags) VALUES (%s, %s, %s)",
            (quote['quote'], quote['author'], ', '.join(quote['tags']))
        )

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()


def upload_author_if_not_exist(name, borndate, bornlocation, description, user_id) -> int:
    a = session.query(Author)\
        .where(and_(Author.fullname == name, Author.user_id==user_id))\
        .first()
    if a:
        # вже існує такий тег
        return a.id
    else:
        # автора не існує - потрібно додати            
        author = Author(
            fullname=name,
            born_date=borndate,
            born_location=bornlocation,
            description=description,
            created=datetime.now(),
            user_id=user_id
        )
        session.add(author)
        session.commit()
        return author.id


def find_author_id(fullname):
    author = session.query(Author).filter(Author.fullname == fullname).first()
    if author:
        return author.id
    return None


def insert_quote_if_not_exist(quote, author_id, user_id) -> int:
    if not author_id or not author_id:
        # якщо автора немає або квота прийшла пуста - не додаємо цитату
        raise ValueError("Author not found in the database")

    q = session.query(Quote)\
        .where(and_(Quote.quote == quote, Author.user_id==user_id))\
        .first()
    if q:
        # вже існує такий тег
        return q.id
    else:
        # квота не існує - потрібно додати
        quote = Quote(
            quote=quote,
            author_id=author_id,
            created=datetime.now(),
            user_id=user_id
        )
        session.add(quote)
        session.commit()
        return quote.id


def insert_tag_if_not_exist(name, user_id) -> int:
    t = session.query(Tag)\
        .where(and_(Tag.name == name, Tag.user_id==user_id))\
        .first()
    if t:
        # вже існує такий тег
        return t.id
    else:
        # новий тег - треба додати в БД
        tag = Tag(
            name=name,
            user_id=user_id
        )
        session.add(tag)
        session.commit()
        return tag.id


def insert_quote_to_tag(quote_id, tag_id) -> int:
    qt = session.query(QuoteToTag)\
        .where(
            and_(
                QuoteToTag.quote_id == quote_id,
                QuoteToTag.tag_id == tag_id
            )
        ).first()
    if qt:
        # вже існує така пара тег-квота
        return qt.id
    else:
        # нова звязка тег-квота - треба додати в БД
        quote_to_tag = QuoteToTag(
            quote_id=quote_id,
            tag_id=tag_id
        )
        session.add(quote_to_tag)
        session.commit()
        return quote_to_tag.id
