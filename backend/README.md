# Tecnoglass – Backend de Trazabilidad de Producción

Django 4.2 + DRF + SQL Server + JWT

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python | 3.11 |
| SQL Server | 2019 / 2022 (local) |
| ODBC Driver | 17 for SQL Server |
| SSMS | cualquiera |

---

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows CMD
# source venv/bin/activate   # Linux / Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar y editar variables de entorno
copy .env.example .env
# Editar .env con tus datos de SQL Server
```

---

## Configurar base de datos

```sql
-- Ejecutar en SSMS
CREATE DATABASE TecnoglassDB;
```

Editar `.env`:

```env
# Autenticación SQL
DB_NAME=TecnoglassDB
DB_HOST=localhost
DB_USER=sa
DB_PASSWORD=tu_password

# O autenticación Windows
# DB_TRUSTED_CONNECTION=yes
# DB_USER=
# DB_PASSWORD=
```

---

## Migraciones y setup inicial

```bash
# Crear tablas
python manage.py migrate

# Sembrar catálogo de estaciones
python manage.py seed_estaciones

# Crear superusuario
python manage.py createsuperuser
```

---

## Stored Procedures

Ejecutar en SSMS **en este orden**:

```
sql/00_ddl_seed_estaciones.sql   (opcional si ya corriste seed_estaciones)
sql/sp_CalcularAvanceOrden.sql
sql/sp_AvanzarVentanaEstacion.sql
sql/sp_ConsultarHistorialVentana.sql
```

---

## Correr el servidor

```bash
python manage.py runserver
# → http://localhost:8000
```

---

## API Endpoints

Todos requieren header `Authorization: Bearer <access_token>` excepto `/api/auth/login`.

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/auth/login/` | Obtener access + refresh token |
| POST | `/api/auth/refresh/` | Renovar access token |
| POST | `/api/ordenes/` | Crear orden + N ventanas (genera QR por cada una) |
| GET  | `/api/ordenes/` | Listar órdenes con % avance |
| GET  | `/api/ordenes/{id}/` | Detalle + distribución por estación |
| GET  | `/api/ventanas/{uuid}/historial/` | Trazabilidad completa de una ventana |
| POST | `/api/ventanas/{uuid}/avanzar/` | Avanzar ventana a siguiente estación |
| GET  | `/api/ventanas/{uuid}/qr/` | URL del QR |
| POST | `/api/ventanas/{uuid}/qr/` | Regenerar QR |
| GET  | `/api/dashboard/resumen/` | Datos agregados para el dashboard |

### Ejemplo – Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Ejemplo – Crear orden

```json
POST /api/ordenes/
{
  "codigo": "ORD-2024-001",
  "total_ventanas": 10
}
```

### Ejemplo – Avanzar estación

```json
POST /api/ventanas/3fa85f64-5717-4562-b3fc-2c963f66afa6/avanzar/
{
  "estacion_destino_id": 1,
  "observaciones": "Sin defectos"
}
```

Respuestas de error estructuradas:

```json
{ "error": "La estación destino no es la siguiente en la secuencia.", "code": "ESTACION_INVALIDA" }
```

| Código HTTP | Code |
|-------------|------|
| 404 | `VENTANA_NO_ENCONTRADA` |
| 404 | `ORDEN_NO_ENCONTRADA` |
| 409 | `ESTACION_INVALIDA` |
| 409 | `VENTANA_YA_EMPACADA` |

---

## Tests

```bash
python manage.py test apps.produccion.tests -v 2
```

Los tests cubren:
- Generación de QR
- Creación de orden + ventanas
- Cálculo de % avance (parcial / 100%)
- Validación de secuencia de estaciones
- Excepción por ventana/orden no encontrada
- Dashboard resumen

---

## Estructura del proyecto

```
backend/
  core/           → settings, urls, exception handler global
  apps/
    usuarios/     → modelo Usuario (AbstractUser + rol), auth JWT
    produccion/   → modelos, servicios, serializers, vistas, tests
      management/commands/seed_estaciones.py
  sql/            → Stored Procedures y seed SQL
  media/          → archivos QR generados (MEDIA_ROOT)
  requirements.txt
  manage.py
```

---

## Notas de concurrencia

`sp_AvanzarVentanaEstacion` usa `WITH (UPDLOCK, HOLDLOCK)` sobre la fila de la ventana.
Si dos operarios escanean la misma ventana simultáneamente:
- El primero adquiere el lock y procesa.
- El segundo espera. Al obtener el lock, lee la ventana ya actualizada y SQL Server lanza `ESTACION_INVALIDA` (no puede avanzar dos veces a la misma estación).

El cálculo de avance de la orden ocurre dentro de la misma transacción → actualización del estado de la orden es atómica con el avance de la ventana.
