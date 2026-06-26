import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { Router } from '@angular/router';
import { OrdenService } from '../../../shared/services/orden.service';
import { OrdenDetail } from '../../../core/models/orden.model';
import { Ventana } from '../../../core/models/ventana.model';
import { MatTableDataSource } from '@angular/material/table';

@Component({
  selector: 'app-orden-detalle',
  templateUrl: './orden-detalle.component.html',
  styleUrls: ['./orden-detalle.component.scss'],
})
export class OrdenDetalleComponent implements OnInit {
  orden:   OrdenDetail | null = null;
  loading  = true;
  error    = false;

  ventanasDS  = new MatTableDataSource<Ventana>();
  ventanaCols = ['identificador_unico', 'estacion_actual', 'empacada', 'acciones'];

  readonly ESTACIONES = ['Corte', 'Troquel', 'Ensamble', 'Empaque'];

  constructor(
    private route:   ActivatedRoute,
    private svc:     OrdenService,
    public  location: Location,
    private router:  Router,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.svc.getById(id).subscribe({
      next: data => {
        this.orden      = data;
        this.ventanasDS = new MatTableDataSource(data.ventanas);
        this.loading    = false;
      },
      error: () => {
        this.error   = true;
        this.loading = false;
      },
    });
  }

  getEstadoClass(estado: string): string {
    return ({ PENDIENTE: 'badge-pendiente', EN_PROCESO: 'badge-proceso', COMPLETADA: 'badge-completada' })[estado] ?? '';
  }

  getEstadoLabel(estado: string): string {
    return ({ PENDIENTE: 'Pendiente', EN_PROCESO: 'En Proceso', COMPLETADA: 'Completada' })[estado] ?? estado;
  }

  getEstacionClass(nombre: string | null): string {
    if (!nombre) return 'badge-sin-iniciar';
    return ({'Corte':'badge-corte','Troquel':'badge-troquel','Ensamble':'badge-ensamble','Empaque':'badge-empaque'})[nombre] ?? '';
  }

  getProgressColor(pct: number): 'primary' | 'accent' | 'warn' {
    return pct >= 100 ? 'primary' : pct > 50 ? 'accent' : 'warn';
  }

  getCount(estacion: string): number {
    return this.orden?.por_estacion[estacion] ?? 0;
  }

  verVentana(v: Ventana): void {
    this.router.navigate(['/ventanas'], { queryParams: { uuid: v.identificador_unico } });
  }

  applyFilter(event: Event): void {
    this.ventanasDS.filter = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
