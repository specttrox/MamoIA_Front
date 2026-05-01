from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
import os

# ----------------------------------------
# Gerenciador de usuários customizado
# ----------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError("O usuário deve ter um endereço de email")
        user = self.model(email=self.normalize_email(email), nome=nome)
        user.set_password(password)  # Criptografa a senha
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password):
        user = self.create_user(email, nome, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# ----------------------------------------
# Modelo de Usuário Customizado
# ----------------------------------------
class User(AbstractBaseUser):
    nome = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    setor = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=128)  # Gerenciado pelo Django
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin


# ----------------------------------------
# Função para padronizar local de upload
# ----------------------------------------
def upload_path(instance, filename):
    # Exemplo: uploads/images/<user_id>/<arquivo>
    return f"uploads/images/{instance.user.id}/{filename}"


# ----------------------------------------
# Modelo de Upload de Imagem Médica
# ----------------------------------------
class MedicalImageUpload(models.Model):
    FILE_TYPES = [
        ("jpg", "Mamografia (JPG)"),
        ("png", "Ultrassom (PNG)"),
        ("jpeg", "Imagem JPEG"),
        ("dcm", "Imagem DICOM"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    file = models.FileField(upload_to=upload_path)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    upload_date = models.DateTimeField(auto_now_add=True)
    report = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-upload_date"]

    def __str__(self):
        nome_arquivo = os.path.basename(self.file.name) if self.file else "sem arquivo"
        return f"{self.user.nome} - {nome_arquivo} ({self.file_type})"

    def generate_report(self):
        """Simulação de um laudo baseado no tipo de arquivo."""
        if self.file_type == "jpg":
            self.report = "Laudo gerado automaticamente para a mamografia."
        elif self.file_type == "png":
            self.report = "Laudo gerado automaticamente para o ultrassom."
        elif self.file_type == "dcm":
            self.report = "Laudo gerado automaticamente para imagem DICOM."
        else:
            self.report = "Laudo gerado para imagem genérica."
        self.save(update_fields=["report"])


# ----------------------------------------
# (Opcional) Modelo de Item (mantido para compatibilidade)
# ----------------------------------------
class Item(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()

    def __str__(self):
        return self.nome
