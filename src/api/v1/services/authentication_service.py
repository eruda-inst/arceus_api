from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from fastapi.exceptions import ValidationException
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, models, schemas
from ..config_core import settings

ALGORITHM = "HS256"
SECRET_KEY = settings.secret_key.get_secret_value()
TOKEN_EXPIRE_MINUTES = settings.token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
TOKEN_EXPIRE_SECONDS = settings.token_expire_seconds


class AuthenticationService:
    @staticmethod
    async def verify_access_token(
        db: AsyncSession, access_token: str
    ) -> models.User | None:
        try:
            payload = jwt.decode(
                token=access_token, key=SECRET_KEY, algorithms=[ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                return None
        except ValidationException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        try:
            user = await cruds.UserCrud.get_by(db=db, email=email)
            return user
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao validar usuário",
            )

    @classmethod
    async def refresh_token(
        cls, refresh_token: schemas.RefreshTokenIn, db: AsyncSession
    ) -> schemas.AccessTokenOut:
        try:
            refresh_token_value = refresh_token.refresh_token
            payload = jwt.decode(
                token=refresh_token_value, key=SECRET_KEY, algorithms=[ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: Email ausente",
                )
        except ValidationException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado. Faça login novamente",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
            )
        user_db = await cruds.UserCrud.get_by(db=db, email=email)
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )
        data = {"sub": email}
        new_access_token = cls._create_token(
            data=data, expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        )
        new_refresh_token = cls._create_token(
            data=data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return schemas.AccessTokenOut(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=TOKEN_EXPIRE_SECONDS,
        )

    @classmethod
    async def login(
        cls, db: AsyncSession, user: schemas.UserLogin
    ) -> schemas.AccessTokenOut:
        try:
            email = user.email
            plain = user.senha.get_secret_value()
            user_db = await cruds.UserCrud.get_by(db=db, email=email)
            if not user_db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email ou senha incorreta",
                )
            is_valid_password = user.verify_senha(plain=plain, hash=str(user_db.senha))
            if not is_valid_password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Falha em login para email: {email}",
                )
            data = {"sub": email}
            access_token = cls._create_token(
                data=data, expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
            )
            refresh_token = cls._create_token(
                data=data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )
            return schemas.AccessTokenOut(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=TOKEN_EXPIRE_SECONDS,
            )
        except ValidationException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Erro de validação durante login",
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro no banco de dados durante login",
            )
        except HTTPException:
            raise

    @staticmethod
    def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
        try:
            to_encode = data.copy()
            expire = datetime.now(ZoneInfo("America/Bahia")) + expires_delta
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(
                claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM
            )
            return encoded_jwt
        except ValidationException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Erro de validação durante criação de token",
            )
