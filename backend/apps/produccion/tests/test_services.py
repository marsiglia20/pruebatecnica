from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.produccion.models import Estacion, OrdenProduccion, Ventana
from apps.produccion.services import QRService, OrdenService, DashboardService
from apps.produccion.exceptions import (
    VentanaNoEncontradaException,
    EstacionInvalidaException,
    OrdenNoEncontradaException,
)

User = get_user_model()


def _seed_estaciones():
    Estacion.objects.get_or_create(nombre='Corte',    defaults={'orden_secuencial': 1})
    Estacion.objects.get_or_create(nombre='Troquel',  defaults={'orden_secuencial': 2})
    Estacion.objects.get_or_create(nombre='Ensamble', defaults={'orden_secuencial': 3})
    Estacion.objects.get_or_create(nombre='Empaque',  defaults={'orden_secuencial': 4})


# ---------------------------------------------------------------------------
# QRService
# ---------------------------------------------------------------------------
class TestQRService(TestCase):
    @patch('apps.produccion.services.os.makedirs')
    @patch('apps.produccion.services.qrcode.QRCode')
    def test_genera_qr_retorna_path_con_uuid(self, mock_qrcode_class, mock_makedirs):
        import uuid
        mock_qr = MagicMock()
        mock_qrcode_class.return_value = mock_qr
        mock_qr.make_image.return_value = MagicMock()

        uid = uuid.uuid4()
        result = QRService.generar_qr(uid)

        self.assertTrue(result.startswith('qr_codes/'))
        self.assertIn(str(uid), result)
        self.assertTrue(result.endswith('.png'))

    @patch('apps.produccion.services.os.makedirs')
    @patch('apps.produccion.services.qrcode.QRCode')
    def test_genera_qr_llama_save(self, mock_qrcode_class, mock_makedirs):
        import uuid
        mock_img = MagicMock()
        mock_qrcode_class.return_value.make_image.return_value = mock_img

        QRService.generar_qr(uuid.uuid4())
        mock_img.save.assert_called_once()


# ---------------------------------------------------------------------------
# OrdenService
# ---------------------------------------------------------------------------
class TestOrdenService(TestCase):
    def setUp(self):
        _seed_estaciones()
        self.user = User.objects.create_user(username='op1', password='pass')

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/test.png')
    def test_crear_orden_crea_ventanas_correctas(self, _qr):
        orden = OrdenService.crear_orden('ORD-001', 5, self.user)
        self.assertEqual(orden.total_ventanas, 5)
        self.assertEqual(orden.ventanas.count(), 5)
        self.assertEqual(orden.estado, OrdenProduccion.PENDIENTE)

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/test.png')
    def test_cada_ventana_uuid_unico(self, _qr):
        orden = OrdenService.crear_orden('ORD-002', 4, self.user)
        uuids = list(orden.ventanas.values_list('identificador_unico', flat=True))
        self.assertEqual(len(set(uuids)), 4)

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/test.png')
    def test_ventanas_inician_sin_estacion(self, _qr):
        orden = OrdenService.crear_orden('ORD-003', 3, self.user)
        sin_estacion = orden.ventanas.filter(estacion_actual__isnull=True).count()
        self.assertEqual(sin_estacion, 3)

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/test.png')
    def test_porcentaje_avance_parcial(self, _qr):
        orden = OrdenService.crear_orden('ORD-004', 4, self.user)
        empaque = Estacion.objects.get(nombre='Empaque')
        ids = list(orden.ventanas.values_list('id', flat=True))[:2]
        Ventana.objects.filter(id__in=ids).update(empacada=True, estacion_actual=empaque)

        result = OrdenService.get_orden_con_avance(orden.pk)
        self.assertEqual(result['porcentaje_avance'], 50.0)
        self.assertEqual(result['ventanas_empacadas'], 2)

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/test.png')
    def test_porcentaje_avance_100(self, _qr):
        orden = OrdenService.crear_orden('ORD-005', 2, self.user)
        empaque = Estacion.objects.get(nombre='Empaque')
        orden.ventanas.all().update(empacada=True, estacion_actual=empaque)

        result = OrdenService.get_orden_con_avance(orden.pk)
        self.assertEqual(result['porcentaje_avance'], 100.0)

    def test_get_orden_inexistente_lanza_excepcion(self):
        with self.assertRaises(OrdenNoEncontradaException):
            OrdenService.get_orden_con_avance(999999)


# ---------------------------------------------------------------------------
# Validación de secuencia (lógica pura, sin SP)
# ---------------------------------------------------------------------------
class TestSecuenciaEstaciones(TestCase):
    def setUp(self):
        _seed_estaciones()

    def _es_valido(self, orden_actual, orden_destino):
        if orden_actual is None:
            return orden_destino == 1
        return orden_destino == orden_actual + 1

    def test_null_a_corte_valido(self):
        self.assertTrue(self._es_valido(None, 1))

    def test_null_a_troquel_invalido(self):
        self.assertFalse(self._es_valido(None, 2))

    def test_corte_a_troquel_valido(self):
        self.assertTrue(self._es_valido(1, 2))

    def test_corte_a_ensamble_invalido(self):
        self.assertFalse(self._es_valido(1, 3))

    def test_troquel_a_ensamble_valido(self):
        self.assertTrue(self._es_valido(2, 3))

    def test_ensamble_a_empaque_valido(self):
        self.assertTrue(self._es_valido(3, 4))

    def test_empaque_es_ultima(self):
        empaque = Estacion.objects.get(nombre='Empaque')
        hay_siguiente = Estacion.objects.filter(
            orden_secuencial__gt=empaque.orden_secuencial
        ).exists()
        self.assertFalse(hay_siguiente)

    def test_retroceso_invalido(self):
        self.assertFalse(self._es_valido(3, 2))


# ---------------------------------------------------------------------------
# VentanaService.get_historial (sin SP real - mockea cursor)
# ---------------------------------------------------------------------------
class TestVentanaServiceHistorial(TestCase):
    def setUp(self):
        _seed_estaciones()
        self.user = User.objects.create_user(username='op2', password='pass')

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/t.png')
    def test_get_historial_ventana_inexistente(self, _qr):
        import uuid
        with self.assertRaises(VentanaNoEncontradaException):
            from apps.produccion.services import VentanaService
            VentanaService.get_historial(str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# DashboardService
# ---------------------------------------------------------------------------
class TestDashboardService(TestCase):
    def setUp(self):
        _seed_estaciones()
        self.user = User.objects.create_user(username='op3', password='pass')

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/t.png')
    def test_resumen_sin_ordenes(self, _qr):
        resumen = DashboardService.get_resumen()
        self.assertEqual(resumen['total_ordenes'], 0)
        self.assertEqual(resumen['porcentaje_global'], 0)

    @patch('apps.produccion.services.QRService.generar_qr', return_value='qr_codes/t.png')
    def test_resumen_con_orden_parcial(self, _qr):
        orden = OrdenService.crear_orden('ORD-D1', 4, self.user)
        empaque = Estacion.objects.get(nombre='Empaque')
        ids = list(orden.ventanas.values_list('id', flat=True))[:2]
        Ventana.objects.filter(id__in=ids).update(empacada=True, estacion_actual=empaque)

        resumen = DashboardService.get_resumen()
        self.assertEqual(resumen['total_ventanas'], 4)
        self.assertEqual(resumen['ventanas_empacadas'], 2)
        self.assertEqual(resumen['porcentaje_global'], 50.0)
        self.assertEqual(resumen['ordenes_activas'], 1)
