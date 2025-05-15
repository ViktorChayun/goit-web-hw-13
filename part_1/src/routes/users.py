# import urllib3
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
# from cloudinary.api_client import _http

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import current_active_user
from src.configuration.config import settings
from src.schemas.schemas import UserDbModel

# disable SSL verification warnings - це лише для розробки, на моєму компі проблема з SSL сертифікатом
# SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain
# urllib3.disable_warnings()

# override cloudinary HTTP object - щоб вимкнути перевірку сертифікату, це не для продакшину, лише для мого компа
# _http.ca_certs = None
# _http.cert_reqs = 'CERT_NONE'

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDbModel)
async def read_users_me(current_user: User = Depends(current_active_user)):
    return current_user


@router.patch('/avatar', response_model=UserDbModel)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(
        file.file,
        public_id=f'NotesApp/{current_user.username}',
        overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
