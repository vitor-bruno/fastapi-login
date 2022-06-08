from pydantic import BaseModel, EmailStr


class BaseUsuario(BaseModel):
    email: EmailStr
    senha_hash: str


class CriarUsuario(BaseUsuario):
    pass


class UsuarioPy(BaseUsuario):
    id: int
    ativo: bool = True

    class Config:
        orm_mode = True