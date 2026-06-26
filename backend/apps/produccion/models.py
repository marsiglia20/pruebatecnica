import uuid
from django.db import models
from django.conf import settings


class Estacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    orden_secuencial = models.IntegerField(unique=True)
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'produccion_estacion'
        ordering = ['orden_secuencial']
        verbose_name = 'Estación'
        verbose_name_plural = 'Estaciones'

    def __str__(self):
        return f"{self.orden_secuencial}. {self.nombre}"


class OrdenProduccion(models.Model):
    PENDIENTE = 'PENDIENTE'
    EN_PROCESO = 'EN_PROCESO'
    COMPLETADA = 'COMPLETADA'

    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (EN_PROCESO, 'En Proceso'),
        (COMPLETADA, 'Completada'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    total_ventanas = models.IntegerField()
    fecha_completada = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ordenes_creadas',
    )

    class Meta:
        db_table = 'produccion_ordenproduccion'
        ordering = ['-fecha_creacion']
        verbose_name = 'Orden de Producción'
        verbose_name_plural = 'Órdenes de Producción'

    def __str__(self):
        return f"{self.codigo} [{self.estado}]"


class Ventana(models.Model):
    identificador_unico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    orden = models.ForeignKey(
        OrdenProduccion,
        on_delete=models.CASCADE,
        related_name='ventanas',
    )
    estacion_actual = models.ForeignKey(
        Estacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ventanas_en_estacion',
    )
    codigo_qr = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    empacada = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'produccion_ventana'
        verbose_name = 'Ventana'
        verbose_name_plural = 'Ventanas'

    def __str__(self):
        return str(self.identificador_unico)


class MovimientoVentana(models.Model):
    ventana = models.ForeignKey(
        Ventana,
        on_delete=models.CASCADE,
        related_name='movimientos',
    )
    estacion = models.ForeignKey(
        Estacion,
        on_delete=models.PROTECT,
        related_name='movimientos',
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimientos_registrados',
    )
    observaciones = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'produccion_movimientoventana'
        ordering = ['fecha_movimiento']
        verbose_name = 'Movimiento de Ventana'
        verbose_name_plural = 'Movimientos de Ventana'

    def __str__(self):
        return f"{self.ventana} → {self.estacion} ({self.fecha_movimiento:%Y-%m-%d %H:%M})"
