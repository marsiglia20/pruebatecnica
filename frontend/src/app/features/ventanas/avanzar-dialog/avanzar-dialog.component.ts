import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface AvanzarDialogData {
  estacionNombre: string;
  estacionId:     number;
  identificador:  string;
}

@Component({
  selector: 'app-avanzar-dialog',
  template: `
    <h2 mat-dialog-title>
      <mat-icon color="primary">arrow_forward</mat-icon>
      Avanzar a {{ data.estacionNombre }}
    </h2>

    <mat-dialog-content>
      <p class="mat-body-1">
        La ventana avanzará a la estación <strong>{{ data.estacionNombre }}</strong>.
        Esta acción no se puede deshacer.
      </p>
      <form [formGroup]="form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Observaciones (opcional)</mat-label>
          <textarea matInput formControlName="observaciones"
                    rows="3" placeholder="Notas del operario..."></textarea>
          <mat-hint align="end">
            {{ form.get('observaciones')?.value?.length ?? 0 }}/500
          </mat-hint>
        </mat-form-field>
      </form>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="confirmar()">
        <mat-icon>check</mat-icon>
        Confirmar Avance
      </button>
    </mat-dialog-actions>
  `,
})
export class AvanzarDialogComponent {
  form: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<AvanzarDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AvanzarDialogData,
  ) {
    this.form = this.fb.group({ observaciones: [''] });
  }

  confirmar(): void {
    this.dialogRef.close(this.form.value.observaciones as string);
  }

  cancelar(): void {
    this.dialogRef.close(null);
  }
}
