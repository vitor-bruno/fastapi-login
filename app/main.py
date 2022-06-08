from datetime import timedelta
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise
from typing import List

from app.utils import (
    autenticar_usuario,
    usuario_ativo,
    token_de_acesso,
    enviar_email_de_redefinicao_de_senha,
    gerar_token_de_redefinicao_de_senha,
    verificar_token_de_senha
    )
    
from app.models import Usuario
from app.schemas import UsuarioPy, CriarUsuario


app = FastAPI()


@app.post('/login')
async def gerar_token_de_acesso(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = await autenticar_usuario(form_data.username, form_data.password)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais incorretas')

    usuario_obj = UsuarioPy.from_orm(usuario)
    tempo_token = timedelta(minutes=30)

    token = token_de_acesso(usuario_obj.dict(), tempo_token)

    return {'access_token' : token, 'token_type' : 'bearer'}


@app.post('/cadastro', response_model=UsuarioPy)
async def registrar_usuario(usuario: CriarUsuario):
    usuario_obj = Usuario(email=usuario.email, senha_hash=bcrypt.hash(usuario.senha_hash))

    await usuario_obj.save()

    return UsuarioPy.from_orm(usuario_obj)


@app.post('/redefinicao-de-senha/{email}')
async def enviar_email_para_redefinir_senha(email: str):
    usuario = await Usuario.get(email=email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado no banco de dados.",
        )

    token = gerar_token_de_redefinicao_de_senha(email=email)

    enviar_email_de_redefinicao_de_senha(destinatario=usuario.email, email=email, token=token)

    return {'msg': 'Email de redefinição de senha enviado com sucesso.'}


@app.post('/alterar-senha')
async def redefinir_senha_com_token(token: str, nova_senha: str):
    email = verificar_token_de_senha(token)

    if not email:
        raise HTTPException(status_code=400, detail="Token Inválido")

    usuario = await Usuario.get(email=email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado no banco de dados.",
        )
    
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    senha_hash = bcrypt.hash(nova_senha)
    usuario.senha_hash = senha_hash
    await usuario.save()
    return {"msg": "Senha atualizada com sucesso"}


@app.get('/usuarios', response_model=List[UsuarioPy])
async def ver_usuarios_cadastrados(skip: int = 0, limit: int = 100, usuario_logado: UsuarioPy = Depends(usuario_ativo)):
    usuarios = await Usuario.all().offset(skip).limit(limit)
    return usuarios


@app.get('/usuario-logado', response_model=UsuarioPy)
async def ver_usuario_logado(usuario_logado: UsuarioPy = Depends(usuario_ativo)):
    return usuario_logado


register_tortoise(
    app,
    db_url = config('DATABASE_URL'),
    modules = {'models' : ['app.models']},
    generate_schemas = True,
    add_exception_handlers = True
)
