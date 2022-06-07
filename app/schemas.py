from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import Usuario


Usuario_Pydantic = pydantic_model_creator(Usuario, name='Usuario')

UsuarioIn_Pydantic = pydantic_model_creator(Usuario, name='UsuarioIn', exclude_readonly=True)