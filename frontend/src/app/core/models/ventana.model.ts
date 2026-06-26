export interface Estacion {
  id: number;
  nombre: string;
  orden_secuencial: number;
}

export interface Ventana {
  id: number;
  identificador_unico: string;
  estacion_actual: Estacion | null;
  codigo_qr_url: string | null;
  empacada: boolean;
  created_at: string;
}

export interface Movimiento {
  id: number;
  estacion_nombre: string;
  estacion_orden: number;
  fecha_movimiento: string;
  usuario_responsable: string;
  nombre_completo: string;
  observaciones: string;
}

export interface VentanaHistorial {
  ventana: Ventana;
  movimientos: Movimiento[];
}

export interface AvanzarEstacionRequest {
  estacion_destino_id: number;
  observaciones?: string;
}
