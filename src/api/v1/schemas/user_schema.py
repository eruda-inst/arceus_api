from datetime import datetime

from argon2 import PasswordHasher
from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt, SecretStr

ph = PasswordHasher()

# Common field definitions (reusable Field objects)
# Required
EmailField = Field(description="E-mail do usuário", examples=["exemplo@exemplo.com"])
SenhaField = Field(min_length=8, description="Senha do usuário", examples=["12345678"])
NomeField = Field(description="Nome do usuário", examples=["Nome do usuário"])
IdGrupoField = Field(ge=1, description="ID do grupo", examples=[1])
NomeGrupoField = Field(description="Nome do grupo", examples=["Administrador"])
AtivoField = Field(default=True, description="Status do usuário", examples=[True])
IdField = Field(ge=1, description="ID do usuário", examples=[1])
CriadoEmField = Field(
    description="Data de criação do usuário", examples=["AAAA-MM-DD HH:MM:SS"]
)
AtualizadoEmField = Field(
    default=None,
    description="Data de atualização do usuário",
    examples=["AAAA-MM-DD HH:MM:SS"],
)
# Optionals
OptNomeField = Field(
    default=None, description="Nome do usuário", examples=["Nome do usuário"]
)
OptAtivoField = Field(default=None, description="Status do usuário", examples=[True])
OptEmailField = Field(
    default=None, description="E-mail do usuário", examples=["exemplo@exemplo.com"]
)
OptSenhaField = Field(
    default=None, min_length=8, description="Senha do usuário", examples=["12345678"]
)
OptIdGrupoField = Field(default=None, ge=1, description="ID do grupo", examples=[1])


class UserLoginSchema(BaseModel):
    email: EmailStr = EmailField
    senha: SecretStr = SenhaField

    @staticmethod
    def verify_senha(plain: str, hash: str) -> bool:
        return ph.verify(password=plain, hash=hash)


class UserInSchema(BaseModel):
    nome: str = NomeField
    senha: SecretStr = SenhaField
    email: EmailStr = EmailField
    id_grupo: PositiveInt = IdGrupoField
    ativo: bool | None = AtivoField

    def get_hash(self) -> str | None:
        if self.senha is None:
            return None
        return ph.hash(password=self.senha.get_secret_value())

    @staticmethod
    def verify_senha(plain: str, hash: str) -> bool:
        return ph.verify(password=plain, hash=hash)


class UserUpdateSchema(BaseModel):
    nome: str | None = OptNomeField
    ativo: bool | None = OptAtivoField
    email: EmailStr | None = OptEmailField
    senha: SecretStr | None = OptSenhaField
    id_grupo: PositiveInt | None = OptIdGrupoField

    def get_hash(self) -> str | None:
        if self.senha is None:
            return None
        return ph.hash(password=self.senha.get_secret_value())


class UserOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = IdField
    nome: str = NomeField
    email: EmailStr = EmailField
    ativo: bool | None = AtivoField
    criado_em: datetime = CriadoEmField
    atualizado_em: datetime | None = AtualizadoEmField
    id_grupo: PositiveInt = IdGrupoField
    nome_grupo: str = NomeGrupoField
