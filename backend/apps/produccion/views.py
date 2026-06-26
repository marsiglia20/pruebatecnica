from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from .models import OrdenProduccion, Ventana
from .serializers import (
    OrdenListSerializer,
    OrdenDetailSerializer,
    CrearOrdenSerializer,
    AvanzarEstacionSerializer,
    VentanaListSerializer,
)
from .services import OrdenService, VentanaService, DashboardService
from .exceptions import VentanaNoEncontradaException


class OrdenListCreateView(generics.ListAPIView):
    queryset = OrdenProduccion.objects.prefetch_related('ventanas').order_by('-fecha_creacion')
    serializer_class = OrdenListSerializer

    def post(self, request):
        serializer = CrearOrdenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orden = OrdenService.crear_orden(
            serializer.validated_data['codigo'],
            serializer.validated_data['total_ventanas'],
            request.user,
        )
        return Response(
            OrdenDetailSerializer(orden, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class OrdenDetailView(generics.RetrieveAPIView):
    queryset = OrdenProduccion.objects.prefetch_related('ventanas')
    serializer_class = OrdenDetailSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Exception:
            from .exceptions import OrdenNoEncontradaException
            raise OrdenNoEncontradaException(self.kwargs.get('pk'))


class VentanaHistorialView(APIView):
    def get(self, request, identificador):
        result = VentanaService.get_historial(str(identificador))
        ventana_data = VentanaListSerializer(
            result['ventana'], context={'request': request}
        ).data
        return Response({'ventana': ventana_data, 'movimientos': result['movimientos']})


class VentanaAvanzarView(APIView):
    def post(self, request, identificador):
        serializer = AvanzarEstacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = VentanaService.avanzar_estacion(
            str(identificador),
            serializer.validated_data['estacion_destino_id'],
            request.user.id,
            serializer.validated_data.get('observaciones'),
        )
        return Response(result)


class VentanaQRView(APIView):
    def get(self, request, identificador):
        try:
            ventana = Ventana.objects.get(identificador_unico=identificador)
        except Ventana.DoesNotExist:
            raise VentanaNoEncontradaException(str(identificador))

        qr_url = None
        if ventana.codigo_qr:
            qr_url = request.build_absolute_uri(ventana.codigo_qr.url)
        return Response({'identificador': str(ventana.identificador_unico), 'qr_url': qr_url})

    def post(self, request, identificador):
        codigo_qr = VentanaService.regenerar_qr(str(identificador))
        qr_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{codigo_qr}')
        return Response({'qr_url': qr_url, 'mensaje': 'QR regenerado exitosamente.'})


class DashboardResumenView(APIView):
    def get(self, request):
        return Response(DashboardService.get_resumen())
