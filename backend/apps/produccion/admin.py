from django.contrib import admin
from .models import Estacion, OrdenProduccion, Ventana, MovimientoVentana


@admin.register(Estacion)
class EstacionAdmin(admin.ModelAdmin):
    list_display = ('orden_secuencial', 'nombre', 'descripcion')
    ordering = ('orden_secuencial',)


@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'estado', 'total_ventanas', 'fecha_creacion', 'fecha_completada')
    list_filter = ('estado',)
    search_fields = ('codigo',)
    readonly_fields = ('fecha_creacion', 'fecha_completada')


@admin.register(Ventana)
class VentanaAdmin(admin.ModelAdmin):
    list_display = ('identificador_unico', 'orden', 'estacion_actual', 'empacada', 'created_at')
    list_filter = ('empacada', 'estacion_actual')
    search_fields = ('identificador_unico',)
    readonly_fields = ('identificador_unico', 'created_at')


@admin.register(MovimientoVentana)
class MovimientoVentanaAdmin(admin.ModelAdmin):
    list_display = ('ventana', 'estacion', 'usuario_responsable', 'fecha_movimiento')
    list_filter = ('estacion',)
    readonly_fields = ('fecha_movimiento',)
