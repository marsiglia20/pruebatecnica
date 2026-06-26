from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_OPERARIO = 'OPERARIO'
    ROL_SUPERVISOR = 'SUPERVISOR'

    ROL_CHOICES = [
        (ROL_OPERARIO, 'Operario'),
        (ROL_SUPERVISOR, 'Supervisor'),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_OPERARIO)

    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.rol})"
