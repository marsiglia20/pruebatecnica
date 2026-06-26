from django.core.management.base import BaseCommand
from apps.produccion.models import Estacion

ESTACIONES = [
    {'nombre': 'Corte',    'orden_secuencial': 1, 'descripcion': 'Corte de perfiles de aluminio'},
    {'nombre': 'Troquel',  'orden_secuencial': 2, 'descripcion': 'Troquelado y perforación de perfiles'},
    {'nombre': 'Ensamble', 'orden_secuencial': 3, 'descripcion': 'Ensamble de marco y vidrio'},
    {'nombre': 'Empaque',  'orden_secuencial': 4, 'descripcion': 'Empaque y etiquetado final'},
]


class Command(BaseCommand):
    help = 'Siembra el catálogo de estaciones (idempotente)'

    def handle(self, *args, **options):
        for data in ESTACIONES:
            obj, created = Estacion.objects.get_or_create(
                orden_secuencial=data['orden_secuencial'],
                defaults=data,
            )
            label = 'Creada' if created else 'Ya existe'
            self.stdout.write(f"  {label}: {obj}")
        self.stdout.write(self.style.SUCCESS('Seed de estaciones completado.'))
