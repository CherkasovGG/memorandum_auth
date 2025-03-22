from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException, status

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.db.repository import DatabaseRepository
from core.fastapi.dependencies import get_repository
from api.auth.generate_password import hash_password
from api.auth.generate_token import JWTService
from app.models.user import User

from .dto import UserResponseDTO, UserCreateDTO
from api.auth.dto import TokenDTO


jwt_service = JWTService()

UserRepository = Annotated[
    DatabaseRepository[User],
    Depends(get_repository(User)),
]

http_bearer_scheme = HTTPBearer()

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get(
    "/",
    response_model=UserResponseDTO,
    responses={
        200: {"description": "User data retrieved successfully."},
        401: {"description": "Unauthorized. Invalid or missing JWT token."},
        404: {"description": "User not found."},
    },
)
async def get_user_route(
    repository: UserRepository,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_scheme),
):
    """
    Get user data. The operation returns the data of the user that is associated with the provided JWT token.
    """
    token = credentials.credentials

    try:
        payload = jwt_service.decode_jwt(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_message": "Invalid or expired token", "error_code": 6},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_message": "Token does not contain user ID", "error_code": 7},
        )

    user = await repository.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_message": "User not found", "error_code": 8},
        )

    return user


@user_router.post(
    "/",
    response_model=UserResponseDTO,
    responses={
        201: {"description": "User created successfully."},
        422: {"description": "Bad request. Invalid input data."},
        409: {"description": "Conflict. User already exists."},
    },
)
async def create_user_route(data: UserCreateDTO, repository: UserRepository):
    """
    Create user. The operation creates new user with provided data.
    """

    if len(await repository.filter(User.email == data.email)) > 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"error_massage": "Такая почта уже существует", "error_code": 1},
        )
    if len(await repository.filter(User.username == data.username)) > 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"error_massage": "Такое имя уже существует", "error_code": 2},
        )

    user = await repository.create(
        {
            "username": data.username,
            "email": data.email,
            "password_hash": hash_password(data.password),
        }
    )

    return UserResponseDTO.model_validate(user)


@user_router.delete(
    "/",
    responses={
        200: {"description": "User deleted successfully."},
        401: {"description": "Unauthorized. Invalid or missing JWT token."},
        404: {"description": "User not found."},
    },
)
async def delete_user_route(
    user_repo: UserRepository,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_scheme),
):
    """
    Delete user. The operation deletes the user associated with the provided JWT token.
    """
    token = credentials.credentials

    try:
        payload = jwt_service.decode_jwt(token)
    except Exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"error_massage": "Invalid or expired token", "error_code": 3},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"error_massage": "Token does not contain user ID", "error_code": 4},
        )

    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            {"error_massage": "User not found", "error_code": 5},
        )

    await user_repo.delete(user_id)

    return {"detail": "User deleted successfully"}
