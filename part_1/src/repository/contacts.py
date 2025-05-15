from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func, and_

from src.database.models import Contact, User
from src.schemas.schemas import ContactSchema


async def get_contacts(
    skip: int,
    limit: int,
    user: User,
    db: Session
) -> List[Contact] | None:
    return db.query(Contact).\
        filter(Contact.user == user).\
        offset(skip).limit(limit).all()


async def get_contact(
    contact_id: int,
    user: User,
    db: Session
) -> Contact | None:
    return db.query(Contact).\
        filter(and_(Contact.id == contact_id, Contact.user == user)).\
        first()


async def craete_contact(
    data: ContactSchema,
    user: User,
    db: Session
) -> Contact:
    new_contact = Contact(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_number=data.phone_number,
        birthday=data.birthday,
        additional_info=data.additional_info,
        user=user
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


async def update_contact(
    contact_id: int,
    data: ContactSchema,
    user: User,
    db: Session
) -> Contact | None:
    contact = db.query(Contact).\
        filter(and_(Contact.id == contact_id, Contact.user == user)).\
        first()
    if contact:
        contact.first_name = data.first_name
        contact.last_name = data.last_name
        contact.email = data.email
        contact.phone_number = data.phone_number
        contact.birthday = data.birthday
        contact.additional_info = data.additional_info
        db.commit()
        db.refresh(contact)
    return contact


async def delete_contact(
    contact_id: int,
    user: User,
    db: Session
) -> Contact | None:
    contact = db.query(Contact).\
        filter(and_(Contact.id == contact_id, Contact.user == user)).\
        first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(
    first_name: Optional[str],
    last_name: Optional[str],
    email: Optional[str],
    user: User,
    skip: int,
    limit: int,
    db: Session
) -> List[Contact]:
    # print(email)
    query = select(Contact)
    query = query.where(Contact.user == user)
    if first_name:
        query = query.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.where(Contact.email.ilike(f"%{email}%"))
    query = query.offset(skip).limit(limit)
    print(query)
    result = db.execute(query)
    return result.scalars().all()


async def upcoming_birthdays(
    days: int,
    skip: int,
    limit: int,
    user: User,
    db: Session
) -> List[Contact]:
    today = date.today()
    filter_lst = {(today + timedelta(days=i)).strftime("%m-%d")
                  for i in range(days)}
    query = select(Contact).where(
        func.to_char(Contact.birthday, 'MM-DD').in_(filter_lst)
    )
    query = query.where(Contact.user == user)
    query = query.offset(skip).limit(limit)
    print(query)
    # result = await db.execute(query)
    result = db.execute(query)
    return result.scalars().all()
