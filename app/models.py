from tortoise.models import Model
from tortoise import fields
from passlib.hash import bcrypt


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(50, unique=True)
    hash_password = fields.CharField(128)
    active_user = fields.BooleanField(default=True)

    def valid_password(self, senha):
        return bcrypt.verify(senha, self.hash_password)