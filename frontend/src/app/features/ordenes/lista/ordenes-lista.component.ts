import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatPaginator } from '@angular/material/paginator';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { OrdenService } from '../../../shared/services/orden.service';
import { Orden } from '../../../core/models/orden.model';
import { CrearOrdenDialogComponent } from '../crear-dialog/crear-orden-dialog.component';

@Component({
  selector: 'app-ordenes-lista',
  templateUrl: './ordenes-lista.component.html',
  styleUrls: ['./ordenes-lista.component.scss'],
})
export class OrdenesListaComponent implements OnInit {
  @ViewChild(MatSort)      sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  dataSource = new MatTableDataSource<Orden>();
  columns    = ['codigo', 'estado', 'total_ventanas', 'avance', 'fecha_creacion', 'acciones'];
  loading    = true;
  filterValue = '';

  constructor(
    private svc:    OrdenService,
    private dialog: MatDialog,
    private snack:  MatSnackBar,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading = true;
    this.svc.getAll().subscribe({
      next: data => {
        this.dataSource.data      = data;
        this.dataSource.sort      = this.sort;
        this.dataSource.paginator = this.paginator;
        this.loading = false;
      },
      error: () => {
        this.snack.open('Error cargando órdenes', 'Cerrar', { duration: 3000 });
        this.loading = false;
      },
    });
  }

  applyFilter(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  crearOrden(): void {
    this.dialog
      .open(CrearOrdenDialogComponent, { width: '420px', disableClose: true })
      .afterClosed()
      .subscribe(created => { if (created) this.cargar(); });
  }

  verDetalle(orden: Orden): void {
    this.router.navigate(['/ordenes', orden.id]);
  }

  getEstadoClass(estado: string): string {
    return ({ PENDIENTE: 'badge-pendiente', EN_PROCESO: 'badge-proceso', COMPLETADA: 'badge-completada' })[estado] ?? '';
  }

  getEstadoLabel(estado: string): string {
    return ({ PENDIENTE: 'Pendiente', EN_PROCESO: 'En Proceso', COMPLETADA: 'Completada' })[estado] ?? estado;
  }

  getProgressColor(pct: number): 'primary' | 'accent' | 'warn' {
    return pct >= 100 ? 'primary' : pct > 50 ? 'accent' : 'warn';
  }
}
