from datetime import datetime, timedelta
from pathlib import Path

import jwt
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

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


async def send_password_reset_email(email_to: str, email: str, token: str):
    conf = ConnectionConfig(
        MAIL_USERNAME=config('SMTP_USER'),
        MAIL_FROM=config('SMTP_USER'),
        MAIL_PASSWORD=config('SMTP_PASSWORD'),
        MAIL_PORT=config('SMTP_PORT'),
        MAIL_SERVER=config('SMTP_HOST'),
        MAIL_TLS=True,
        MAIL_SSL=False,
        TEMPLATE_FOLDER = Path(__file__).parent / 'templates'
    )
    
    mensagem = MessageSchema(
       subject=f"Redefinição de senha para o usuário {email}",
       recipients=[email_to],
       template_body={
            "email": email,
            "valid_hours": 48,
            "token": token,
        },
       subtype="html"
       )
    
    fm = FastMail(conf)
    await fm.send_message(mensagem, template_name='password_reset.html')
