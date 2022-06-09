from datetime import datetime, timedelta
from typing import Any, Dict

import emails
import jwt
from decouple import config
from emails.template import JinjaTemplate
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models import User
from app.schemas import UserPydantic

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

JWT_SECRET = config('JWT_SECRET')
ALGORITHM = "HS256"


async def authenticated_user(email: str, password: str):
    user = await User.get(email=email)
    
    if not user:
        return False
    
    if not user.valid_password(password):
        return False

    return user


async def active_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM)
        user = await User.get(id=payload.get('id'))
    
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais incorretas')
    
    if not user.active_user:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    return UserPydantic.from_orm(user)


def access_token(user_dict: dict, token_exp: timedelta):
    data = user_dict.copy()
    
    data.update({"exp" : datetime.utcnow() + token_exp})

    token = jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)
    
    return token


def password_reset_token(email: str):
    delta = timedelta(hours=48)
    now = datetime.utcnow()
    exp = (now + delta).timestamp()

    token = jwt.encode({"exp": exp, "nbf": now, "sub": email}, JWT_SECRET, algorithm=ALGORITHM)
    return token


def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM)
        return payload.get("sub")
    except:
        return None


def send_email(email_to: str, subject: str = "", template: str = "", context: Dict[str, Any] = {}):
    message = emails.Message(
        subject=JinjaTemplate(subject),
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

    message.send(to=email_to, render=context, smtp=smtp_options)


def send_password_reset_email(email_to: str, email: str, token: str):
    subject = f"Redefinição de senha para o usuário {email}"

    with open("app/templates/password_reset.html") as f:
        template_str = f.read()

    link = f"http://127.0.0.1:8000/alterar-senha?token={token}"
    
    send_email(
        email_to=email_to,
        subject=subject,
        template=template_str,
        context={
            "email": email,
            "valid_hours": 48,
            "link": link,
        },
    )
