from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas.schemas import ContactSchema
from src.repository import contacts as rep_contacts
from src.services.auth import current_active_user


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "",
    response_model=List[ContactSchema],
    dependencies=[Depends(RateLimiter(times=1, seconds=2))]
)
async def read_contacts(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(100, ge=1, le=1000),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    if first_name is not None or last_name is not None or email is not None:
        # шукаємо контакти, якщо було вказано пошукові фільтри
        contacts = await rep_contacts.search_contacts(
            first_name,
            last_name,
            email,
            skip,
            limit,
            user,
            db
        )
    else:
        # просто повертаємо список контактів
        contacts = await rep_contacts.get_contacts(skip, limit, user, db)

    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacts are not found.")

    return contacts


@router.get(
    "/upcoming_birthdays",
    response_model=List[ContactSchema],
    dependencies=[Depends(RateLimiter(times=1, seconds=2))]
)
async def get_upcoming_birthdays(
    days: Optional[int] = Query(7, ge=1, le=365),
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(100, ge=1, le=1000),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    # print(f"{days}, {skip}, {limit}")
    contacts = await rep_contacts.upcoming_birthdays(
        days, skip, limit, user, db
    )
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birthday's contacts are not found."
        )
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=2))]
)
async def read_contact(
    contact_id: int = Path(ge=1),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    contact = await rep_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact id = {contact_id} is not found.")
    return contact


@router.post(
    "",
    response_model=ContactSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=2))],
    status_code=status.HTTP_201_CREATED
)
async def create_contact(
    data: ContactSchema,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    return await rep_contacts.craete_contact(data, user, db)


@router.put(
    "/{contact_id}",
    response_model=ContactSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=2))]
)
async def update_contact(
    data: ContactSchema,
    contact_id: int = Path(ge=1),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    contact = await rep_contacts.update_contact(contact_id, data, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact id = {contact_id} is not found."
        )
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=2))]
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    contact = await rep_contacts.delete_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact id = {contact_id} is not found."
        )
    return contact
