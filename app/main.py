from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from typing import List

from .utils import (
    authenticated_user,
    active_user,
    access_token,
    send_password_reset_email,
    password_reset_token,
    verify_password_reset_token
    )
    
from .models import User
from .schemas import UserPydantic, CreateUser


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["fastapi-login.herokuapp.com", "127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post('/login')
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticated_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais incorretas')

    user_obj = UserPydantic.from_orm(user)
    token_exp = timedelta(minutes=30)

    token = access_token(user_obj.dict(), token_exp)

    return {'access_token' : token, 'token_type' : 'bearer'}


@app.post('/signup', response_model=UserPydantic)
async def register_new_user(user: CreateUser):
    user_obj = User(email=user.email, hash_password=bcrypt.hash(user.hash_password))

    await user_obj.save()

    return UserPydantic.from_orm(user_obj)


@app.post('/forgot-password/{email}')
async def send_token_for_password_reset(email: str):
    user = await User.get(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado no banco de dados.",
        )

    token = password_reset_token(email=email)

    await send_password_reset_email(email_to=user.email, email=email, token=token)

    return {"mensagem" : "Email enviado com sucesso"}


@app.post('/reset-password')
async def password_reset_from_token(token: str, new_password: str):
    email = verify_password_reset_token(token)

    if not email:
        raise HTTPException(status_code=400, detail="Token Inválido")

    user = await User.get(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado no banco de dados.",
        )
    
    if not user.active_user:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    hash_password = bcrypt.hash(new_password)
    user.hash_password = hash_password
    await user.save()
    return {"msg": "Senha atualizada com sucesso"}


@app.get('/users', response_model=List[UserPydantic])
async def get_registered_users(skip: int = 0, limit: int = 100, active_user: UserPydantic = Depends(active_user)):
    users = await User.all().offset(skip).limit(limit)
    return users


@app.get('/users/me', response_model=UserPydantic)
async def get_current_user(active_user: UserPydantic = Depends(active_user)):
    return active_user


Tortoise.init_models(["app.models"], "models")
register_tortoise(
    app,
    db_url = config('DATABASE_URL'),
    modules = {'models' : ['app.models']},
    generate_schemas = True,
    add_exception_handlers = True
)
