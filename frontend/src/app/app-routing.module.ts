import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard }            from './core/guards/auth.guard';

import { LoginComponent }            from './features/auth/login/login.component';
import { DashboardComponent }        from './features/dashboard/dashboard.component';
import { OrdenesListaComponent }     from './features/ordenes/lista/ordenes-lista.component';
import { OrdenDetalleComponent }     from './features/ordenes/detalle/orden-detalle.component';
import { BuscarVentanaComponent }    from './features/ventanas/buscar/buscar-ventana.component';

const routes: Routes = [
  { path: 'login',     component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent,    canActivate: [AuthGuard] },
  { path: 'ordenes',   component: OrdenesListaComponent, canActivate: [AuthGuard] },
  { path: 'ordenes/:id', component: OrdenDetalleComponent, canActivate: [AuthGuard] },
  { path: 'ventanas',  component: BuscarVentanaComponent, canActivate: [AuthGuard] },
  { path: '',          redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**',        redirectTo: '/dashboard' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
