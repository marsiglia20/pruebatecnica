import { Ventana } from './ventana.model';

export interface Orden {
  id: number;
  codigo: string;
  estado: 'PENDIENTE' | 'EN_PROCESO' | 'COMPLETADA';
  total_ventanas: number;
  porcentaje_avance: number;
  ventanas_empacadas: number;
  fecha_creacion: string;
  fecha_completada: string | null;
}

export interface OrdenDetail extends Orden {
  por_estacion: Record<string, number>;
  ventanas: Ventana[];
}

export interface CrearOrdenRequest {
  codigo: string;
  total_ventanas: number;
}
