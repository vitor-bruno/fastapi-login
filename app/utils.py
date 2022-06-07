import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from decouple import config
from fastapi.security import OAuth2PasswordBearer

from app.models import Usuario
from app.schemas import Usuario_Pydantic


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

JWT_SECRET = config('JWT_SECRET')
ALGORITHM = "HS256"


async def autenticar_usuario(nome_de_usuario: str, senha: str):
    usuario = await Usuario.get(nome_de_usuario=nome_de_usuario)
    
    if not usuario:
        return False
    
    if not usuario.senha_valida(senha):
        return False

    return usuario


async def usuario_ativo(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM)
        usuario = await Usuario.get(id=payload.get('id'))
    
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais incorretas')
    
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    return await Usuario_Pydantic.from_tortoise_orm(usuario)


def token_de_acesso(usuario_dict: dict, tempo_token: timedelta):
    dados = usuario_dict.copy()
    
    dados.update({"exp" : datetime.utcnow() + tempo_token})

    token = jwt.encode(dados, JWT_SECRET, algorithm=ALGORITHM)
    
    return token