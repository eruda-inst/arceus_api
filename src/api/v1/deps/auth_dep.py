"""
Authentication and authorization dependencies for FastAPI endpoints.

Provides dependencies for:
- Retrieving the current user from a Bearer token.
- Validating Basic Auth credentials for bot access.
- Checking if a user has a required permission.
"""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt  # whatever you use
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config, cruds, db, models, services, utils

# Security schemes
basic_security = HTTPBasic()
bearer_security = HTTPBearer()


async def get_curr_user(
    db: Annotated[AsyncSession, Depends(db.get_db)],
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> models.UserModel:
    """
    Dependency to retrieve the currently authenticated user from a Bearer token.

    Args:
        db: Database session.
        creds: Bearer token credentials extracted from the Authorization header.

    Returns:
        The authenticated UserModel instance.

    Raises:
        HTTPException: 401 if the token is invalid or the user does not exist.
    """
    access_token = creds.credentials
    # Verify the access token and fetch the associated user
    user = await services.AuthService.verify_access_token(
        db=db, access_token=access_token
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou usuário inexistente",
        )
    return user


def get_creds(
    creds: Annotated[HTTPBasicCredentials, Depends(basic_security)],
) -> bool:
    """
    Dependency to validate Basic Auth credentials for bot access.

    Compares the provided username and password against the configured bot
    credentials using constant-time comparison to prevent timing attacks.

    Args:
        creds: Basic Auth credentials extracted from the Authorization header.

    Returns:
        True if credentials are valid.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    # Encode provided credentials
    cred_username = creds.username.encode()
    cred_pass = creds.password.encode()

    # Encode configured bot credentials
    config_username = config.settings.bot_username.encode()
    config_pass = config.settings.bot_pass.get_secret_value().encode()

    # Use constant-time comparison to avoid timing attacks
    valid_username = secrets.compare_digest(cred_username, config_username)
    valid_password = secrets.compare_digest(cred_pass, config_pass)

    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


def has_perm(req_perm: utils.PermCodes):
    """
    Dependency factory to check if the current user has a required permission.

    Args:
        req_perm: The permission code required to access the endpoint.

    Returns:
        A dependency function that returns the current user if they have the permission.

    Raises:
        HTTPException: 403 if the user does not have the required permission.
    """

    async def dep(
        db: Annotated[AsyncSession, Depends(db.get_db)],
        curr_user: Annotated[models.UserModel, Depends(get_curr_user)],
    ) -> models.UserModel:
        """
        Inner dependency that performs the permission check.

        Args:
            db: Database session.
            curr_user: The currently authenticated user.

        Returns:
            The current user if they have the required permission.

        Raises:
            HTTPException: 403 if permission is missing.
        """
        # Fetch all permissions for the current user
        _, user_perms = await cruds.PermCrud.get_all_by(db=db, id_usuario=curr_user.id)  # type: ignore

        # Extract permission codes
        perm_codes = [p.codigo for p in user_perms]
        if req_perm not in perm_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {req_perm}",
            )
        return curr_user

    return dep


async def get_curr_user_ws(
    ws: WebSocket,
    session: Annotated[AsyncSession, Depends(db.get_db)],
) -> models.UserModel:
    """
    Dependency to retrieve the currently authenticated user from a WebSocket connection.

    The token can be provided either as a `token` query parameter or in the
    `Authorization: Bearer <token>` header. The query parameter takes precedence.

    Args:
        ws: The active WebSocket connection.
        session: Database session.

    Returns:
        The authenticated UserModel instance.

    Raises:
        WebSocketException: 1008 if the token is missing, malformed, invalid,
            or the user does not exist.
    """
    # Prefer the token from the query string, e.g. ws://...?token=...
    token = ws.query_params.get("token")

    # Fall back to the Authorization header if no query token was provided
    if not token:
        auth = ws.headers.get("authorization") or ""
        scheme, _, header_token = auth.partition(" ")
        if scheme.lower() != "bearer" or not header_token:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Cabeçalho de autorização faltando ou malformado",
            )
        token = header_token

    try:
        # Decode and validate the JWT using the configured secret
        payload = jwt.decode(
            token=token,
            key=config.settings.secret_key.get_secret_value(),
            algorithms=["HS256"],
        )

        # The subject (`sub`) is expected to contain the user's email
        user = await cruds.UserCrud.get_by(db=session, email=payload["sub"])
    except (JWTError, KeyError):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token inválido",
        )

    # Ensure the token refers to an existing user
    if user is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Usuário inexistente",
        )

    return user
