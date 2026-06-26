import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { CommonModule } from '@angular/common';

import { AppMaterialModule } from './app-material.module';
import { AppRoutingModule }  from './app-routing.module';

import { JwtInterceptor }  from './core/interceptors/jwt.interceptor';

// Components
import { AppComponent }         from './app.component';
import { NavbarComponent }      from './shared/components/navbar/navbar.component';
import { LoginComponent }       from './features/auth/login/login.component';
import { DashboardComponent }   from './features/dashboard/dashboard.component';
import { OrdenesListaComponent }     from './features/ordenes/lista/ordenes-lista.component';
import { OrdenDetalleComponent }     from './features/ordenes/detalle/orden-detalle.component';
import { CrearOrdenDialogComponent } from './features/ordenes/crear-dialog/crear-orden-dialog.component';
import { BuscarVentanaComponent }    from './features/ventanas/buscar/buscar-ventana.component';
import { AvanzarDialogComponent }    from './features/ventanas/avanzar-dialog/avanzar-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    LoginComponent,
    DashboardComponent,
    OrdenesListaComponent,
    OrdenDetalleComponent,
    CrearOrdenDialogComponent,
    BuscarVentanaComponent,
    AvanzarDialogComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    AppMaterialModule,
    AppRoutingModule,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
