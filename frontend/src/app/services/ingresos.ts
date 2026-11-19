
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Ingreso {
  id: number;
  categoria: number;
  presupuesto: number | null;
  monto: string;
  fecha: string;
  descripcion: string;
  creado: string;
}

@Injectable({
  providedIn: 'root'
})
export class Ingresos {
  private http = inject(HttpClient);
  private apiUrl = '/api/ingresos/';

  listar(): Observable<Ingreso[]> {
    return this.http.get<Ingreso[]>(this.apiUrl);
  }

  crear(ingreso: {
    categoria: number;
    presupuesto: number | null;
    monto: number;
    fecha: string;
    descripcion: string;
  }): Observable<Ingreso> {
    return this.http.post<Ingreso>(this.apiUrl, ingreso);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}
