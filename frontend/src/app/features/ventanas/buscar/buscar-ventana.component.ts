import { Component, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { VentanaService } from '../../../shared/services/ventana.service';
import { VentanaHistorial, Estacion } from '../../../core/models/ventana.model';
import { AvanzarDialogComponent } from '../avanzar-dialog/avanzar-dialog.component';

const UUID_PATTERN = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

@Component({
  selector: 'app-buscar-ventana',
  templateUrl: './buscar-ventana.component.html',
  styleUrls: ['./buscar-ventana.component.scss'],
})
export class BuscarVentanaComponent implements OnInit {
  uuidCtrl = new FormControl('', [Validators.required, Validators.pattern(UUID_PATTERN)]);

  historial:    VentanaHistorial | null = null;
  loading       = false;
  searching     = false;
  errorMsg:     string | null = null;
  qrUrl:        string | null = null;
  showQr        = false;

  readonly ESTACIONES = ['Corte', 'Troquel', 'Ensamble', 'Empaque'];
  movCols = ['estacion_nombre', 'fecha_movimiento', 'usuario_responsable', 'observaciones'];

  constructor(
    private svc:    VentanaService,
    private dialog: MatDialog,
    private snack:  MatSnackBar,
    private route:  ActivatedRoute,
  ) {}

  ngOnInit(): void {
    const uuid = this.route.snapshot.queryParamMap.get('uuid');
    if (uuid) {
      this.uuidCtrl.setValue(uuid);
      this.buscar();
    }
  }

  buscar(): void {
    if (this.uuidCtrl.invalid) return;
    this.searching = true;
    this.historial = null;
    this.errorMsg  = null;
    this.qrUrl     = null;
    this.showQr    = false;

    this.svc.getHistorial(this.uuidCtrl.value!).subscribe({
      next: data => {
        this.historial  = data;
        this.searching  = false;
      },
      error: err => {
        this.errorMsg  = err.error?.error ?? 'Ventana no encontrada.';
        this.searching = false;
      },
    });
  }

  get estacionActualIdx(): number {
    const nombre = this.historial?.ventana.estacion_actual?.nombre;
    return nombre ? this.ESTACIONES.indexOf(nombre) : -1;
  }

  get siguienteEstacion(): { id: number; nombre: string } | null {
    if (!this.historial) return null;
    const { ventana } = this.historial;
    if (ventana.empacada) return null;

    const actual = ventana.estacion_actual;
    if (!actual) {
      return { id: 1, nombre: 'Corte' };
    }
    const nextOrder = actual.orden_secuencial + 1;
    const map: Record<number, { id: number; nombre: string }> = {
      2: { id: 2, nombre: 'Troquel' },
      3: { id: 3, nombre: 'Ensamble' },
      4: { id: 4, nombre: 'Empaque' },
    };
    return map[nextOrder] ?? null;
  }

  avanzar(): void {
    const next = this.siguienteEstacion;
    if (!next || !this.historial) return;

    this.dialog
      .open(AvanzarDialogComponent, {
        width: '450px',
        data: {
          estacionNombre: next.nombre,
          estacionId:     next.id,
          identificador:  this.historial.ventana.identificador_unico,
        },
      })
      .afterClosed()
      .subscribe((obs: string | null) => {
        if (obs === null) return;

        this.loading = true;
        this.svc.avanzar(this.historial!.ventana.identificador_unico, {
          estacion_destino_id: next.id,
          observaciones: obs || undefined,
        }).subscribe({
          next: () => {
            this.snack.open(`✓ Ventana avanzó a ${next.nombre}`, '', { duration: 3000 });
            this.buscar();
            this.loading = false;
          },
          error: err => {
            this.snack.open(err.error?.error ?? 'Error al avanzar', 'Cerrar', { duration: 5000 });
            this.loading = false;
          },
        });
      });
  }

  verQR(): void {
    if (!this.historial) return;
    this.svc.getQR(this.historial.ventana.identificador_unico).subscribe({
      next: resp => {
        this.qrUrl  = resp.qr_url;
        this.showQr = true;
      },
      error: () => this.snack.open('No se pudo cargar el QR', 'Cerrar', { duration: 3000 }),
    });
  }

  getEstacionClass(nombre: string | null): string {
    if (!nombre) return 'badge-sin-iniciar';
    return ({ Corte:'badge-corte', Troquel:'badge-troquel', Ensamble:'badge-ensamble', Empaque:'badge-empaque' })[nombre] ?? '';
  }
}
