import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Gasto {
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
export class Gastos {
  private http = inject(HttpClient);
  private apiUrl = '/api/gastos/';

  listar(): Observable<Gasto[]> {
    return this.http.get<Gasto[]>(this.apiUrl);
  }

  crear(gasto: {
    categoria: number;
    presupuesto: number | null;
    monto: number;
    fecha: string;
    descripcion: string;
  }): Observable<Gasto> {
    return this.http.post<Gasto>(this.apiUrl, gasto);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}