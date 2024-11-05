from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from schemas import (
    ResponseAuthTokens,
    ResponseMessage,
    ResponseUserHistory,
    ResponseUserPermissions,
    UserCredentials,
    UserPassUpdate,
    UserRegistration,
)
from services.auth import AuthException, IAsyncAuthService, get_auth_service
from services.provider import ProviderService, SocialException, get_provider_service
from starlette.requests import Request

if TYPE_CHECKING:
    from models.user_provider import UserProvider

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


@router.get("/history", response_model=ResponseUserHistory, summary="История входов")
async def history(
    access_token: str = Depends(oauth2_scheme),
    auth_service: IAsyncAuthService = Depends(get_auth_service),
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth_service.user_history(access_token)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.patch("/password_change", summary="Смена пароля")
async def password_change(
    user: UserPassUpdate, auth_service: IAsyncAuthService = Depends(get_auth_service)
):
    try:
        await auth_service.password_change(user)
        return {"success": True, "message": "Password is changed"}
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register",
    response_model=ResponseMessage,
    summary="Регистрация пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserRegistration,
    user_agent: Annotated[str | None, Header()] = None,
    auth_service: IAsyncAuthService = Depends(get_auth_service),
):
    try:
        await auth_service.register(user, user_agent)
        return ResponseMessage(
            message="Registration successful. Please log in using /login."
        )
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/authorize/{provider}",
    response_model=ResponseAuthTokens,
    status_code=status.HTTP_200_OK,
    summary="Регистрация или авторизация пользователя через oAuth 2.0 провайдеров",
    include_in_schema=False,
)
async def authorize_provider(
    provider: str,
    request: Request,
    user_agent: Annotated[str | None, Header()] = None,
    auth_service: IAsyncAuthService = Depends(get_auth_service),
    social_service: ProviderService = Depends(get_provider_service),
):
    try:
        user: UserProvider = await social_service.authorize(
            provider_name=provider, request=request
        )
    except SocialException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    try:
        return await auth_service.authorize_provider(user=user, user_agent=user_agent)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/login",
    response_model=ResponseAuthTokens,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
)
async def login(
    user: UserCredentials,
    user_agent: Annotated[str | None, Header()] = None,
    auth_service: IAsyncAuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.login(user, user_agent)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/login/{provider}", include_in_schema=False)
async def login_provider(
    provider: str, provider_service: ProviderService = Depends(get_provider_service)
):
    try:
        return RedirectResponse(
            url=provider_service.get_authorization_url(provider_name=provider)
        )
    except SocialException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/token/refresh",
    response_model=ResponseAuthTokens,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов",
)
async def refresh_tokens(
    refresh_token: str = Header(None),
    user_agent: Annotated[str | None, Header()] = None,
    auth_service: IAsyncAuthService = Depends(get_auth_service),
) -> ResponseAuthTokens:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await auth_service.refresh_tokens(
            refresh_token=refresh_token, user_agent=user_agent
        )
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete(
    "/logout",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Выйти из сессии на одном устройстве",
)
async def user_logout(
    access_token: str = Depends(oauth2_scheme),
    auth_service: IAsyncAuthService = Depends(get_auth_service),
) -> ResponseMessage:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        await auth_service.logout(access_token=access_token)
        return ResponseMessage(message="Logged out")
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete(
    "/logout_all",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Выйти из сессии на всех устройствах",
)
async def user_logout_all(
    access_token: str = Depends(oauth2_scheme),
    auth_service: IAsyncAuthService = Depends(get_auth_service),
) -> ResponseMessage:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        await auth_service.logout_from_all_devices(access_token=access_token)
        return ResponseMessage(message="Logged out from all devices")
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/token/validate",
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Проверить валидность access токена",
)
async def validate(
    access_token: str = Depends(oauth2_scheme),
    auth_service: IAsyncAuthService = Depends(get_auth_service),
) -> ResponseMessage:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        if await auth_service.validate_access_token(access_token=access_token):
            return ResponseMessage(message="Token is valid.")

    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/permissions",
    response_model=ResponseUserPermissions,
    summary="Пермишены пользователя",
)
async def history_permissions(
    access_token: str = Depends(oauth2_scheme),
    auth_service: IAsyncAuthService = Depends(get_auth_service),
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth_service.user_permissions(access_token)
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
