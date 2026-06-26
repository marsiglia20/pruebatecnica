import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { VentanaHistorial, AvanzarEstacionRequest } from '../../core/models/ventana.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class VentanaService {
  private readonly base = `${environment.apiUrl}/ventanas`;

  constructor(private http: HttpClient) {}

  getHistorial(uuid: string): Observable<VentanaHistorial> {
    return this.http.get<VentanaHistorial>(`${this.base}/${uuid}/historial/`);
  }

  avanzar(uuid: string, data: AvanzarEstacionRequest): Observable<Record<string, unknown>> {
    return this.http.post<Record<string, unknown>>(`${this.base}/${uuid}/avanzar/`, data);
  }

  getQR(uuid: string): Observable<{ qr_url: string; identificador: string }> {
    return this.http.get<{ qr_url: string; identificador: string }>(`${this.base}/${uuid}/qr/`);
  }

  regenerarQR(uuid: string): Observable<{ qr_url: string; mensaje: string }> {
    return this.http.post<{ qr_url: string; mensaje: string }>(`${this.base}/${uuid}/qr/`, {});
  }
}
