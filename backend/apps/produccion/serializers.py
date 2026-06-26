from rest_framework import serializers
from .models import Estacion, OrdenProduccion, Ventana, MovimientoVentana


class EstacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estacion
        fields = ['id', 'nombre', 'orden_secuencial']


class VentanaListSerializer(serializers.ModelSerializer):
    estacion_actual = EstacionSerializer(read_only=True)
    codigo_qr_url = serializers.SerializerMethodField()

    class Meta:
        model = Ventana
        fields = [
            'id', 'identificador_unico', 'estacion_actual',
            'codigo_qr_url', 'empacada', 'created_at',
        ]

    def get_codigo_qr_url(self, obj):
        request = self.context.get('request')
        if obj.codigo_qr and request:
            return request.build_absolute_uri(obj.codigo_qr.url)
        return None


class OrdenListSerializer(serializers.ModelSerializer):
    porcentaje_avance = serializers.SerializerMethodField()
    ventanas_empacadas = serializers.SerializerMethodField()

    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'codigo', 'estado', 'total_ventanas',
            'porcentaje_avance', 'ventanas_empacadas',
            'fecha_creacion', 'fecha_completada',
        ]

    def get_porcentaje_avance(self, obj):
        empacadas = obj.ventanas.filter(empacada=True).count()
        return round((empacadas / obj.total_ventanas * 100) if obj.total_ventanas else 0, 2)

    def get_ventanas_empacadas(self, obj):
        return obj.ventanas.filter(empacada=True).count()


class OrdenDetailSerializer(serializers.ModelSerializer):
    porcentaje_avance = serializers.SerializerMethodField()
    ventanas_empacadas = serializers.SerializerMethodField()
    por_estacion = serializers.SerializerMethodField()
    ventanas = VentanaListSerializer(many=True, read_only=True)

    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'codigo', 'estado', 'total_ventanas',
            'porcentaje_avance', 'ventanas_empacadas',
            'fecha_creacion', 'fecha_completada',
            'por_estacion', 'ventanas',
        ]

    def get_porcentaje_avance(self, obj):
        empacadas = obj.ventanas.filter(empacada=True).count()
        return round((empacadas / obj.total_ventanas * 100) if obj.total_ventanas else 0, 2)

    def get_ventanas_empacadas(self, obj):
        return obj.ventanas.filter(empacada=True).count()

    def get_por_estacion(self, obj):
        result = {'sin_iniciar': obj.ventanas.filter(estacion_actual__isnull=True).count()}
        for est in Estacion.objects.all().order_by('orden_secuencial'):
            result[est.nombre] = obj.ventanas.filter(estacion_actual=est).count()
        return result


class CrearOrdenSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=50)
    total_ventanas = serializers.IntegerField(min_value=1, max_value=10000)

    def validate_codigo(self, value):
        if OrdenProduccion.objects.filter(codigo=value).exists():
            raise serializers.ValidationError(f"Ya existe una orden con código '{value}'.")
        return value


class AvanzarEstacionSerializer(serializers.Serializer):
    estacion_destino_id = serializers.IntegerField()
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_estacion_destino_id(self, value):
        if not Estacion.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Estación con id={value} no existe.")
        return value


class MovimientoSerializer(serializers.ModelSerializer):
    estacion = EstacionSerializer(read_only=True)
    usuario_responsable = serializers.StringRelatedField()

    class Meta:
        model = MovimientoVentana
        fields = ['id', 'estacion', 'fecha_movimiento', 'usuario_responsable', 'observaciones']
