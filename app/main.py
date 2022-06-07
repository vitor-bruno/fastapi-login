from datetime import timedelta
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise

from app.utils import autenticar_usuario, usuario_ativo, token_de_acesso
from app.models import Usuario
from app.schemas import Usuario_Pydantic, UsuarioIn_Pydantic


app = FastAPI()


@app.post('/login')
async def gerar_token_de_acesso(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = await autenticar_usuario(form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais incorretas')

    usuario_obj = await Usuario_Pydantic.from_tortoise_orm(usuario)
    tempo_token = timedelta(minutes=30)

    token = token_de_acesso(usuario_obj.dict(), tempo_token)

    return {'access_token' : token, 'token_type' : 'bearer'}


@app.post('/cadastro', response_model=Usuario_Pydantic)
async def registrar_usuario(usuario: UsuarioIn_Pydantic):
    usuario_obj = Usuario(nome_de_usuario=usuario.nome_de_usuario, senha_hash=bcrypt.hash(usuario.senha_hash))

    await usuario_obj.save()

    return await Usuario_Pydantic.from_tortoise_orm(usuario_obj)


@app.get('/usuarios/me', response_model=Usuario_Pydantic)
async def ver_usuario_logado(usuario_logado: Usuario_Pydantic = Depends(usuario_ativo)):
    return usuario_logado


register_tortoise(
    app,
    db_url = config('DATABASE_URL'),
    modules = {'models' : ['app.models']},
    generate_schemas = True,
    add_exception_handlers = True
)
