# Tecnoglass – Frontend Angular

Angular 16 + Angular Material + Chart.js

---

## Setup (primera vez)

```bash
# 1. Instalar Angular CLI globalmente si no está
npm install -g @angular/cli@16

# 2. Crear el proyecto scaffold (una sola vez)
cd "c:\Users\USUARIO\OneDrive\Documentos\Prueba Tecnoglass"
ng new tecnoglass-angular --routing --style=scss --skip-tests --skip-git
cd tecnoglass-angular

# 3. Copiar el contenido de esta carpeta (frontend/) reemplazando src/
# Copiar manualmente:
#   frontend/src/           → tecnoglass-angular/src/
#   frontend/package.json   → tecnoglass-angular/package.json (merge devDeps)

# 4. Instalar dependencias
npm install

# 5. Agregar Angular Material (si no está en el proyecto)
ng add @angular/material
# Elegir: Indigo/Pink → No global typography → Yes browser animations

# 6. Correr
ng serve
# → http://localhost:4200
```

---

## Configuración rápida

El único archivo que posiblemente necesitas editar es:

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',  // ← URL del backend Django
};
```

---

## Rutas de la app

| Ruta | Componente | Descripción |
|------|-----------|-------------|
| `/login` | LoginComponent | Autenticación JWT |
| `/dashboard` | DashboardComponent | KPIs globales + chart |
| `/ordenes` | OrdenesListaComponent | Tabla de órdenes + crear |
| `/ordenes/:id` | OrdenDetalleComponent | Detalle + distribución por estación |
| `/ventanas?uuid=...` | BuscarVentanaComponent | Consulta + historial + avanzar |

---

## Estructura

```
src/app/
  core/
    models/          → Interfaces TypeScript (auth, orden, ventana, dashboard)
    services/        → AuthService
    guards/          → AuthGuard (protege rutas)
    interceptors/    → JwtInterceptor (Bearer token automático)
  shared/
    services/        → OrdenService, VentanaService, DashboardService
    components/
      navbar/        → Barra de navegación con links y logout
  features/
    auth/login/      → Login form
    dashboard/       → KPIs + barchart Chart.js
    ordenes/
      lista/         → MatTable con filtro, sort, paginator, progress bars
      detalle/       → Info orden + distribución estaciones + tabla ventanas
      crear-dialog/  → MatDialog para nueva orden
    ventanas/
      buscar/        → Buscar por UUID + stepper + timeline + avanzar
      avanzar-dialog/→ Confirmación de avance con campo observaciones
  app-material.module.ts → Todos los imports de Angular Material
```

---

## Flujo de uso

### 1. Login
- Usuario y contraseña → JWT almacenado en localStorage
- Redirección automática a `/dashboard`

### 2. Crear Orden
- Ir a **Órdenes** → botón **Nueva Orden**
- Ingresar código (ej. `ORD-2024-001`) y cantidad de ventanas
- El backend genera QR para cada ventana automáticamente

### 3. Avanzar Ventana
- Ir a **Ventanas** → ingresar UUID (o escanear QR con pistola/teclado)
- Botón **Avanzar a [Siguiente Estación]**
- Confirmar en el diálogo (observaciones opcionales)

### 4. Dashboard
- Actualización manual con el botón refresh
- Chart.js muestra ventanas por estación en tiempo real

---

## CORS

El backend Django ya tiene `corsheaders` configurado para `http://localhost:4200`.
Si el frontend corre en otro puerto, editar `CORS_ORIGINS` en el `.env` del backend.
