from core.logger import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jwt_manager.exception import JWTException
from pydantic import conint
from schemas import ResponseMessage, Role, UserRole
from services.exception import AccessException, RoleException
from services.roles import IAsyncRoles, get_role_service

logger = get_logger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             summary='Создание роли')
async def create_role(role: Role,
                      access_token: str = Depends(oauth2_scheme),
                      role_service: IAsyncRoles = Depends(get_role_service)):
    logger.info(f"Creating a new role:{role.name}")
    try:
        role = await role_service.create_role(role=role, access_token=access_token)
        return {"message": f"Role {role.name} created successfully"}, status.HTTP_201_CREATED

    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message)
    except JWTException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message)


@router.delete('/{role_name}',
               response_model=ResponseMessage,
               status_code=status.HTTP_200_OK,
               summary='Удаление роли по названию',
               )
async def delete_role(role_name: str,
                      access_token: str = Depends(oauth2_scheme),
                      role_service: IAsyncRoles = Depends(get_role_service)) -> ResponseMessage:
    logger.info(f"Role {role_name} deleted successfully")

    try:
        await role_service.delete_role_by_name(role_name=role_name, access_token=access_token)
        return ResponseMessage(message=f"Role {role_name} deleted successfully")
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message)
    except AccessException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message)


@router.get('/',
            status_code=status.HTTP_200_OK,
            response_model=list[Role],
            summary='Просмотр всех ролей роли')
async def read_roles(
        limit: conint(ge=1, le=50) | None = Query(None),
        offset: conint(ge=1, le=50) | None = Query(None),
        role_service: IAsyncRoles = Depends(get_role_service)):
    try:
        return await role_service.get_roles(limit=limit, offset=offset)
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message)


@router.get('/{role_name}',
            status_code=status.HTTP_200_OK,
            response_model=Role,
            summary='Просмотр роли')
async def read_role(role_name: str,
                    role_service: IAsyncRoles = Depends(get_role_service)):
    try:
        return await role_service.get_role_by_name(role_name=role_name)
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message)


@router.put('/{role_name}',
            response_model=ResponseMessage,
            status_code=status.HTTP_200_OK,
            summary='Изменение роли' )
async def update_role(
        role_name: str,
        role: Role,
        access_token: str = Depends(oauth2_scheme),
        role_service: IAsyncRoles = Depends(get_role_service)
) -> ResponseMessage:
    logger.info(f"Changing the role:{role_name}")
    try:
        role = await role_service.update_role(role=role, access_token=access_token)
        return ResponseMessage(message=f"The role {role_name} was successfully changed")
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message)


@router.post('/{role_name}/assign',
             response_model=ResponseMessage,
             status_code=status.HTTP_200_OK,
             summary='Назначение роли пользователю')
async def assign_role_to_user(
        role_name: str,
        user_role: UserRole,
        access_token: str = Depends(oauth2_scheme),
        role_service: IAsyncRoles = Depends(get_role_service)) -> ResponseMessage:
    logger.info(f"Assigning role {user_role.user_name} to user {user_role.role_name}")
    try:
        await role_service.assign_role_to_user(user_name=user_role.user_name,
                                               role_name=user_role.role_name,
                                               access_token=access_token)

        message = f"Role {user_role.role_name} assigned to user {user_role.user_name} successfully"
        return ResponseMessage(message=message)
    except AccessException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message)
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message)


@router.post('/{role_name}/revoke',
             response_model=ResponseMessage,
             status_code=status.HTTP_200_OK,
             summary='Забрать роль у пользователя')
async def revoke_role_from_user(
        role_name: str,
        user_role: UserRole,
        access_token: str = Depends(oauth2_scheme),
        role_service: IAsyncRoles = Depends(get_role_service)) -> ResponseMessage:
    logger.info(f"Revoking role {user_role.role_name} from user {user_role.user_name}")
    try:
        await role_service.revoke_role_from_user(user_name=user_role.user_name,
                                                 role_name=user_role.role_name,
                                                 access_token=access_token)
        message = f"Role {user_role.role_name} revoked from user {user_role.user_name} successfully"
        return ResponseMessage(message=message)
    except AccessException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message)
    except RoleException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message)
