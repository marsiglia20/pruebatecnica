import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { OrdenService } from '../../../shared/services/orden.service';

@Component({
  selector: 'app-crear-orden-dialog',
  templateUrl: './crear-orden-dialog.component.html',
})
export class CrearOrdenDialogComponent {
  form: FormGroup;
  loading = false;

  constructor(
    private fb:      FormBuilder,
    private svc:     OrdenService,
    private snack:   MatSnackBar,
    public dialogRef: MatDialogRef<CrearOrdenDialogComponent>,
  ) {
    this.form = this.fb.group({
      codigo:         ['', [Validators.required, Validators.maxLength(50)]],
      total_ventanas: [null, [Validators.required, Validators.min(1), Validators.max(10000)]],
    });
  }

  crear(): void {
    if (this.form.invalid) return;
    this.loading = true;

    this.svc.crear(this.form.value).subscribe({
      next: orden => {
        this.snack.open(
          `Orden ${orden.codigo} creada con ${orden.total_ventanas} ventanas.`,
          '',
          { duration: 4000 },
        );
        this.dialogRef.close(true);
      },
      error: err => {
        const msg = err.error?.codigo?.[0] ?? err.error?.error ?? 'Error al crear la orden.';
        this.snack.open(msg, 'Cerrar', { duration: 5000 });
        this.loading = false;
      },
    });
  }

  cancelar(): void {
    this.dialogRef.close(false);
  }
}
