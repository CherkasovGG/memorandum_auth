from typing import Annotated
from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.fastapi.dependencies import get_repository

from .dto import TokenResponseDTO, TokenRequestDTO
from core.db.repository import DatabaseRepository
from app.models.user import User
from api.auth.generate_password import validate_password
from api.auth.generate_token import JWTService


jwt_service = JWTService()

http_bearer_scheme = HTTPBearer()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

UserRepository = Annotated[
    DatabaseRepository[User],
    Depends(get_repository(User)),
]

@auth_router.post(
    "/token",
    response_model=TokenResponseDTO,
    responses={
        200: {"description": "Token generated successfully."},
        403: {"description": "Forbidden. Invalid credentials."},
        500: {"description": "Server error. Unable to generate token."},
    },
)
async def get_token_route(
    request: TokenRequestDTO,
    user_repo: UserRepository,
):
    """
    Get token. The operation returns JWT token.
    """
    users = await user_repo.filter(User.email == request.email)
    if not users:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            {"error_message": "Forbidden. Invalid credentials.", "error_code": 1},
        )
    user = users[0]

    try:
        if not validate_password(request.password, user.password_hash):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                {"error_message": "Forbidden. Invalid credentials.", "error_code": 2},
            )
    except Exception as e:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            {
                "error_message": f"Forbidden. Invalid credentials. Error: {str(e)}",
                "error_code": 3,
            },
        )

    token = jwt_service.encode_jwt({"sub": str(user.id)})
    return TokenResponseDTO(access_token=token, token_type="bearer")


@auth_router.get(
    "/verify",
    responses={
        200: {"description": "Token is valid."},
        401: {"description": "Invalid token."},
        500: {"description": "Server error during verification."},
    },
)
def verify_token_route(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_scheme),
    response: Response = Response(),
):
    """
    Verify token. The operation verifies provided JWT token and sends user ID in response header 'x-user-id'.
    """
    token = credentials.credentials
    try:
        payload = jwt_service.decode_jwt(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload does not contain 'sub'.",
            )

        response.headers["X-User-Id"] = str(user_id)

        return {"message": "Token is valid."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token. Error: {str(e)}",
        )
