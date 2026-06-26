import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Orden, OrdenDetail, CrearOrdenRequest } from '../../core/models/orden.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class OrdenService {
  private readonly base = `${environment.apiUrl}/ordenes`;

  constructor(private http: HttpClient) {}

  getAll(): Observable<Orden[]> {
    return this.http.get<Orden[]>(`${this.base}/`);
  }

  getById(id: number): Observable<OrdenDetail> {
    return this.http.get<OrdenDetail>(`${this.base}/${id}/`);
  }

  crear(data: CrearOrdenRequest): Observable<OrdenDetail> {
    return this.http.post<OrdenDetail>(`${this.base}/`, data);
  }
}
