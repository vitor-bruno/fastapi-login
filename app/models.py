from tortoise.models import Model
from tortoise import fields
from passlib.hash import bcrypt


class Usuario(Model):
    id = fields.IntField(pk=True)
    nome_de_usuario = fields.CharField(50, unique=True)
    senha_hash = fields.CharField(128)
    ativo = fields.BooleanField(default=True)

    def senha_valida(self, senha):
        return bcrypt.verify(senha, self.senha_hash)