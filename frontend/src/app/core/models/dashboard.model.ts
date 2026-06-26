export interface DashboardResumen {
  total_ordenes: number;
  ordenes_activas: number;
  ordenes_completadas: number;
  total_ventanas: number;
  ventanas_empacadas: number;
  porcentaje_global: number;
  ventanas_por_estacion: Record<string, number>;
}
