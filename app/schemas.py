from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr
    hash_password: str


class CreateUser(BaseUser):
    pass


class UserPydantic(BaseUser):
    id: int
    active_user: bool = True

    class Config:
        orm_mode = True