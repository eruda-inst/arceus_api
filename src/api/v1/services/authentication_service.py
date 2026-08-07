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
    async def verify_access_token(db: AsyncSession, access_token: str) -> models.User:
        try:
            payload = jwt.decode(
                token=access_token, key=SECRET_KEY, algorithms=[ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: e-mail ausente",
                )
            version_from_token = payload.get("ver")
            if version_from_token is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Token inválido: versão ausente"
                )

            user = await cruds.UserCrud.get_by(db=db, email=email)
            if not user:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inexistente")

            if user.versao_token != version_from_token:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Token revogado (logout realizado)"
                )
            if not bool(user.ativo):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário inativo")

            return user
        except ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expirado")
        except JWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
        except SQLAlchemyError:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Erro interno ao validar usuário"
            )

    @classmethod
    async def refresh_token(
        cls, refresh_token: str, db: AsyncSession
    ) -> schemas.AccessTokenOut:
        try:
            payload = jwt.decode(
                token=refresh_token, key=SECRET_KEY, algorithms=[ALGORITHM]
            )
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Token inválido: Email ausente"
                )
            version_from_token = payload.get("ver")
            if version_from_token is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Token inválido: versão ausente"
                )

            user_db = await cruds.UserCrud.get_by(db=db, email=email)
            if not user_db:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inexistente")

            if user_db.versao_token != version_from_token:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Refresh token revogado"
                )
            if not bool(user_db.ativo):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário inativo")

        except ExpiredSignatureError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Refresh token expirado. Faça login novamente",
            )
        except JWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido")

        data = {"sub": email}
        new_access_token = cls._create_token(
            data=data,
            expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            version=user_db.versao_token,  # type: ignore
        )
        new_refresh_token = cls._create_token(
            data=data,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            version=user_db.versao_token,  # type: ignore
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
                    status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos"
                )

            if not user.verify_senha(plain=plain, hash=str(user_db.senha)):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos"
                )

            if not bool(user_db.ativo):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário inativo")

            data = {"sub": email}
            access_token = cls._create_token(
                data=data,
                expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES),
                version=user_db.versao_token,  # type: ignore
            )
            refresh_token = cls._create_token(
                data=data,
                expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                version=user_db.versao_token,  # type: ignore
            )
            return schemas.AccessTokenOut(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=TOKEN_EXPIRE_SECONDS,
            )

        except ValidationException:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Erro de validação durante login"
            )
        except SQLAlchemyError:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Erro no banco de dados durante login",
            )
        except HTTPException:
            raise

    @staticmethod
    def _create_token(
        data: dict[str, Any], expires_delta: timedelta, version: int
    ) -> str:
        to_encode = data.copy()
        to_encode["ver"] = version
        expire = datetime.now(ZoneInfo("America/Bahia")) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
