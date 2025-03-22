from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreateDTO(UserBase):
    password: str


class UserResponseDTO(UserBase):
    id: UUID
