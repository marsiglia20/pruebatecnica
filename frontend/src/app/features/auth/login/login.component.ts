import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  form: FormGroup;
  loading     = false;
  hidePass    = true;

  constructor(
    private fb:     FormBuilder,
    private auth:   AuthService,
    private router: Router,
    private snack:  MatSnackBar,
  ) {
    this.form = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;

    this.auth.login(this.form.value).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: () => {
        this.snack.open('Credenciales incorrectas. Verificar usuario y contraseña.', 'Cerrar', {
          duration: 4000,
          panelClass: 'snack-error',
        });
        this.loading = false;
      },
    });
  }
}
