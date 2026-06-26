import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardResumen } from '../../core/models/dashboard.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(private http: HttpClient) {}

  getResumen(): Observable<DashboardResumen> {
    return this.http.get<DashboardResumen>(`${environment.apiUrl}/dashboard/resumen/`);
  }
}
