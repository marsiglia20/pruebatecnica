export interface LoginRequest {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  nombre_completo: string;
  rol: 'OPERARIO' | 'SUPERVISOR';
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}
