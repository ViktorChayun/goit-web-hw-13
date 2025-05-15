# from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.schemas import UserModel, UserResponseModel, TokenModel, RequestEmail, ResetPasswordRequest
from src.repository import users as rep_users
from src.services.auth import auth_service
from src.services.email import send_verificatoin_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserResponseModel,
    status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_task: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    exist_user = await rep_users.get_user_by_email(body.email, db)
    # exist_user = await auth_service.get_current_user(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await rep_users.create_user(body, db)
    background_task.add_task(
        send_verificatoin_email,
        new_user.email,
        new_user.username,
        request.base_url
    )
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation."
    }


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = await rep_users.get_user_by_email(body.username, db)
    # user = await auth_service.get_current_user(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your mailbox."
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    await rep_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    # user = await rep_users.get_user_by_email(email, db)
    user = await auth_service.get_current_user(email, db)

    if user.refresh_token != token:
        await rep_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(
        data={"sub": email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": email}
    )
    await rep_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await rep_users.get_user_by_email(email, db)
    # user = await auth_service.get_current_user(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error"   
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await rep_users.confirmed_email(email, db)
    return {"message": "Email is successfuly confirmed"}


@router.post('/request-email-verification')
async def request_email_verification(
    body: RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    user = await rep_users.get_user_by_email(body.email, db)
    # user = await auth_service.get_current_user(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_task.add_task(
            send_verificatoin_email,
            user.email,
            user.username,
            request.base_url
        )
    return {"message": "Check your mailbox for confirmation."}


@router.post('/request-reset-password')
async def request_reset_password(
    body: RequestEmail,
    background_task: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    запит на скидання паролю
    """
    user = await rep_users.get_user_by_email(body.email, db)
    # user = await auth_service.get_current_user(body.email, db)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User is not found"
        )
    background_task.add_task(
            send_reset_password_email,
            user.email,
            user.username,
            request.base_url
        )
    return {"message": "Check your mailbox to continue resetting your password on web-site."}


@router.post('/reset-password')
async def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    логіка скидання паролю
    """
    email = await auth_service.get_email_from_token(body.token)
    print(email)
    user = await rep_users.get_user_by_email(email, db)
    # user = await auth_service.get_current_user(email, db)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User is not found"
        )

    hashed_password = auth_service.get_password_hash(body.new_password)
    await rep_users.update_user_password(user, hashed_password, db)
    return {"message": "Password is successfully updated."}
