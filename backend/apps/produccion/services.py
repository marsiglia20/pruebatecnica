import uuid
import os
import qrcode
from django.conf import settings
from django.db import connection, DatabaseError, transaction

from .models import Estacion, OrdenProduccion, Ventana
from .exceptions import (
    VentanaNoEncontradaException,
    EstacionInvalidaException,
    VentanaYaEmpacadaException,
    EstacionNoEncontradaException,
    OrdenNoEncontradaException,
)


def _map_db_error(exc: DatabaseError):
    msg = str(exc)
    if 'VENTANA_NO_ENCONTRADA' in msg:
        raise VentanaNoEncontradaException()
    if 'VENTANA_YA_EMPACADA' in msg:
        raise VentanaYaEmpacadaException()
    if 'ESTACION_NO_ENCONTRADA' in msg:
        raise EstacionNoEncontradaException()
    if 'ESTACION_INVALIDA' in msg:
        detail = msg.split('ESTACION_INVALIDA:')[-1].strip().rstrip("'").strip()
        raise EstacionInvalidaException(detail)


class QRService:
    @staticmethod
    def generar_qr(identificador_unico: uuid.UUID) -> str:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(str(identificador_unico))
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)

        filename = f'{identificador_unico}.png'
        img.save(os.path.join(qr_dir, filename))
        return f'qr_codes/{filename}'


class OrdenService:
    @staticmethod
    @transaction.atomic
    def crear_orden(codigo: str, total_ventanas: int, created_by) -> OrdenProduccion:
        orden = OrdenProduccion.objects.create(
            codigo=codigo,
            total_ventanas=total_ventanas,
            created_by=created_by,
            estado=OrdenProduccion.PENDIENTE,
        )
        ventanas = []
        for _ in range(total_ventanas):
            uid = uuid.uuid4()
            codigo_qr = QRService.generar_qr(uid)
            ventanas.append(Ventana(
                identificador_unico=uid,
                orden=orden,
                codigo_qr=codigo_qr,
            ))
        Ventana.objects.bulk_create(ventanas)
        return orden

    @staticmethod
    def get_orden_con_avance(orden_id: int) -> dict:
        try:
            orden = OrdenProduccion.objects.prefetch_related('ventanas').get(pk=orden_id)
        except OrdenProduccion.DoesNotExist:
            raise OrdenNoEncontradaException(orden_id)

        ventanas_qs = orden.ventanas.all()
        empacadas = ventanas_qs.filter(empacada=True).count()
        total = orden.total_ventanas
        porcentaje = round((empacadas / total * 100) if total > 0 else 0, 2)

        por_estacion = {'sin_iniciar': ventanas_qs.filter(estacion_actual__isnull=True).count()}
        for est in Estacion.objects.all().order_by('orden_secuencial'):
            por_estacion[est.nombre] = ventanas_qs.filter(estacion_actual=est).count()

        return {
            'orden': orden,
            'porcentaje_avance': porcentaje,
            'ventanas_empacadas': empacadas,
            'por_estacion': por_estacion,
        }


class VentanaService:
    @staticmethod
    def avanzar_estacion(
        identificador: str,
        estacion_destino_id: int,
        usuario_id: int,
        observaciones: str = None,
    ) -> dict:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'EXEC sp_AvanzarVentanaEstacion %s, %s, %s, %s',
                    [identificador, estacion_destino_id, usuario_id, observaciones],
                )
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
            return dict(zip(columns, row))
        except DatabaseError as exc:
            _map_db_error(exc)
            raise

    @staticmethod
    def get_historial(identificador: str) -> dict:
        try:
            ventana = Ventana.objects.select_related('orden', 'estacion_actual').get(
                identificador_unico=identificador
            )
        except Ventana.DoesNotExist:
            raise VentanaNoEncontradaException(identificador)
        except Exception:
            raise VentanaNoEncontradaException(identificador)

        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC sp_ConsultarHistorialVentana %s', [identificador])
                columns = [col[0] for col in cursor.description]
                movimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except DatabaseError as exc:
            _map_db_error(exc)
            raise

        return {'ventana': ventana, 'movimientos': movimientos}

    @staticmethod
    def regenerar_qr(identificador: str) -> str:
        try:
            ventana = Ventana.objects.get(identificador_unico=identificador)
        except Ventana.DoesNotExist:
            raise VentanaNoEncontradaException(identificador)

        codigo_qr = QRService.generar_qr(ventana.identificador_unico)
        ventana.codigo_qr = codigo_qr
        ventana.save(update_fields=['codigo_qr'])
        return codigo_qr


class DashboardService:
    @staticmethod
    def get_resumen() -> dict:
        ordenes = OrdenProduccion.objects.all()
        total_ordenes = ordenes.count()
        completadas = ordenes.filter(estado=OrdenProduccion.COMPLETADA).count()
        activas = ordenes.filter(
            estado__in=[OrdenProduccion.PENDIENTE, OrdenProduccion.EN_PROCESO]
        ).count()

        total_ventanas = Ventana.objects.count()
        total_empacadas = Ventana.objects.filter(empacada=True).count()
        porcentaje_global = round(
            (total_empacadas / total_ventanas * 100) if total_ventanas > 0 else 0, 2
        )

        ventanas_por_estacion = {
            'sin_iniciar': Ventana.objects.filter(estacion_actual__isnull=True).count()
        }
        for est in Estacion.objects.all().order_by('orden_secuencial'):
            ventanas_por_estacion[est.nombre] = Ventana.objects.filter(
                estacion_actual=est
            ).count()

        return {
            'total_ordenes': total_ordenes,
            'ordenes_activas': activas,
            'ordenes_completadas': completadas,
            'total_ventanas': total_ventanas,
            'ventanas_empacadas': total_empacadas,
            'porcentaje_global': porcentaje_global,
            'ventanas_por_estacion': ventanas_por_estacion,
        }
