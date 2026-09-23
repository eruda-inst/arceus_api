"""
Service for authentication-related operations.

Handles JWT token verification, refresh, and login.
"""

import datetime as dt
from typing import Any, Final
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from fastapi.exceptions import ValidationException
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import NonNegativeInt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config, cruds, models, schemas

# JWT configuration constants
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[NonNegativeInt] = (
    config.settings.jwt_refresh_token_expire_days
)
JWT_ALGORITHM: Final[str] = config.settings.jwt_algorithm
JWT_REFRESH_TOKEN_EXPIRE_DAYS: Final[NonNegativeInt] = (
    config.settings.jwt_refresh_token_expire_days
)
JWT_SECRET_KEY: Final[str] = config.settings.jwt_secret_key.get_secret_value()
JWT_TOKEN_EXPIRE_SECONDS: Final[NonNegativeInt] = (
    config.settings.jwt_token_expire_seconds
)


class AuthService:
    """
    Provides static/class methods for authentication operations.
    """

    @staticmethod
    async def verify_access_token(
        db: AsyncSession, access_token: str
    ) -> models.UserModel:
        """
        Verify an access token and return the associated user.

        Checks the token signature, expiration, subject (email), token version,
        and whether the user is active.

        Args:
            db: Async database session.
            access_token: The JWT access token to verify.

        Returns:
            The authenticated UserModel instance.

        Raises:
            HTTPException: 401 for invalid/expired tokens or revoked versions.
            HTTPException: 403 if the user is inactive.
            HTTPException: 500 on database errors.
        """
        try:
            payload = jwt.decode(
                token=access_token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
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

            # Ensure the token version matches the current user version
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
    ) -> schemas.AccessTokenOutSchema:
        """
        Refresh an access token using a valid refresh token.

        Args:
            refresh_token: The JWT refresh token.
            db: Async database session.

        Returns:
            A new AccessTokenOutSchema with a fresh access and refresh token.

        Raises:
            HTTPException: 401 for invalid/expired/revoked refresh tokens.
            HTTPException: 403 if the user is inactive.
        """
        try:
            payload = jwt.decode(
                token=refresh_token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
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
        # Issue a new pair of access and refresh tokens
        new_access_token = cls._create_token(
            data=data,
            expires_delta=dt.timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            version=user_db.versao_token,  # type: ignore
        )
        new_refresh_token = cls._create_token(
            data=data,
            expires_delta=dt.timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            version=user_db.versao_token,  # type: ignore
        )
        return schemas.AccessTokenOutSchema(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=JWT_TOKEN_EXPIRE_SECONDS,
        )

    @classmethod
    async def login(
        cls, db: AsyncSession, user: schemas.UserLoginSchema
    ) -> schemas.AccessTokenOutSchema:
        """
        Authenticate a user and return access/refresh tokens.

        Args:
            db: Async database session.
            user: Login credentials (email and password).

        Returns:
            AccessTokenOutSchema containing the tokens and expiry.

        Raises:
            HTTPException: 401 for wrong credentials.
            HTTPException: 403 if the user is inactive.
            HTTPException: 422 for validation errors.
            HTTPException: 500 on database errors.
        """
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
                expires_delta=dt.timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                version=user_db.versao_token,  # type: ignore
            )
            refresh_token = cls._create_token(
                data=data,
                expires_delta=dt.timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
                version=user_db.versao_token,  # type: ignore
            )
            return schemas.AccessTokenOutSchema(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=JWT_TOKEN_EXPIRE_SECONDS,
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
        data: dict[str, Any], expires_delta: dt.timedelta, version: int
    ) -> str:
        """
        Create a signed JWT token.

        Args:
            data: Base claims to include in the token (e.g., subject).
            expires_delta: Time delta until the token expires.
            version: Token version to embed for revocation checks.

        Returns:
            The encoded JWT string.
        """
        to_encode = data.copy()
        to_encode["ver"] = version
        expire = dt.datetime.now(ZoneInfo(config.settings.timezone)) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(claims=to_encode, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
