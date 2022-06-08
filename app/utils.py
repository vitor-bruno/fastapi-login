import jwt
import emails
from typing import Any, Dict
from emails.template import JinjaTemplate
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from decouple import config
from fastapi.security import OAuth2PasswordBearer

from app.models import Usuario
from app.schemas import UsuarioPy


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

JWT_SECRET = config('JWT_SECRET')
ALGORITHM = "HS256"


async def autenticar_usuario(email: str, senha: str):
    usuario = await Usuario.get(email=email)
    
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

    return UsuarioPy.from_orm(usuario)


def token_de_acesso(usuario_dict: dict, tempo_token: timedelta):
    dados = usuario_dict.copy()
    
    dados.update({"exp" : datetime.utcnow() + tempo_token})

    token = jwt.encode(dados, JWT_SECRET, algorithm=ALGORITHM)
    
    return token


def enviar_email(destinatario: str, assunto: str = "", template: str = "", contexto: Dict[str, Any] = {}):
    mensagem = emails.Message(
        subject=JinjaTemplate(assunto),
        html=JinjaTemplate(template),
        mail_from=("Vitor Bruno", "vbruno0110@gmail.com"),
    )

    smtp_options = {
        "host": config('SMTP_HOST'),
        "port": config('SMTP_PORT'),
        "user" : config('SMTP_USER'),
        "password" : config('SMTP_PASSWORD'),
        "tls" : True
        }

    mensagem.send(to=destinatario, render=contexto, smtp=smtp_options)


def gerar_token_de_redefinicao_de_senha(email: str):
    delta = timedelta(hours=48)
    now = datetime.utcnow()
    exp = (now + delta).timestamp()

    token = jwt.encode({"exp": exp, "nbf": now, "sub": email}, config('JWT_SECRET'), algorithm="HS256")
    return token


def enviar_email_de_redefinicao_de_senha(destinatario: str, email: str, token: str):
    assunto = f"Redefinição de senha para o usuário {email}"

    with open("app/templates/redefinicao_senha.html") as f:
        template_str = f.read()

    link = f"http://127.0.0.1:8000/alterar-senha?token={token}"
    
    enviar_email(
        destinatario=destinatario,
        assunto=assunto,
        template=template_str,
        contexto={
            "email": email,
            "valid_hours": 48,
            "link": link,
        },
    )


def verificar_token_de_senha(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM)
        return payload.get("sub")
    except:
        return None