import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { LoginRequest, LoginResponse, User } from '../models/auth.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY   = 'tg_access';
  private readonly REFRESH_KEY = 'tg_refresh';
  private readonly USER_KEY    = 'tg_user';

  private user$ = new BehaviorSubject<User | null>(this.loadUser());

  constructor(private http: HttpClient, private router: Router) {}

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login/`, credentials)
      .pipe(
        tap(resp => {
          localStorage.setItem(this.TOKEN_KEY,   resp.access);
          localStorage.setItem(this.REFRESH_KEY, resp.refresh);
          localStorage.setItem(this.USER_KEY,    JSON.stringify(resp.user));
          this.user$.next(resp.user);
        }),
      );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.user$.next(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  get currentUser$(): Observable<User | null> {
    return this.user$.asObservable();
  }

  get currentUser(): User | null {
    return this.user$.value;
  }

  private loadUser(): User | null {
    const raw = localStorage.getItem(this.USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  }
}
