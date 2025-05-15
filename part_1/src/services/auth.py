from typing import Optional
from datetime import datetime, timedelta
import redis
import pickle

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as rep_users
from src.configuration.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    cache = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({
            "iat": datetime.now(),
            "exp": expire,
            "scope": "access_token"
        })
        encoded_access_token = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_access_token

    async def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=7)
        to_encode.update({
            "iat": datetime.now(),
            "exp": expire,
            "scope": "access_token"
        })
        encoded_refresh_token = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(
                refresh_token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            if payload:
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    async def get_current_user(
        self,
        token: str = Depends(oauth2_schema),
        db: Session = Depends(get_db)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"www-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.cache.get(f"user:{email}")
        if user is None:
            user = await rep_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(f"user:{email}", pickle.dumps(user))
            self.cache.expire(f"user:{email}", settings.redis_cache_timeout)
        else:
            user = pickle.loads(user)
        return user

    async def create_email_token(self, data: dict):
        """
        токен, що використовується для верифікації email
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=7)
        to_encode.update({
            "iat": datetime.now(),
            "exp": expire
        })
        # print(to_encode)
        token = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        # print(token)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            email = payload["sub"]
            return email
        except JWTError as err:
            print(err)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification"
            )

    async def create_password_reset_token(self, data: dict):
        """
        токен, що використовується для скидання паролю
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({
            "iat": datetime.now(),
            "exp": expire
        })
        # print(to_encode)
        token = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        # print(token)
        return token


auth_service = Auth()

current_active_user = auth_service.get_current_user
