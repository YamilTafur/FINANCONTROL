
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface RespuestaLogin {
  mensaje: string;
  usuario: string;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private http = inject(HttpClient);

  obtenerCsrf(): Observable<{ mensaje: string }> {
    return this.http.get<{ mensaje: string }>('/api/csrf/');
  }

  iniciarSesion(username: string, password: string): Observable<RespuestaLogin> {
    return this.http.post<RespuestaLogin>('/api/login/', {
      username,
      password
    });
  }

  cerrarSesion(): Observable<{ mensaje: string }> {
    return this.http.post<{ mensaje: string }>('/api/logout/', {});
  }
}
