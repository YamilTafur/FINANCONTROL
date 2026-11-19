
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Presupuesto {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  monto_limite: string | number;
  creado: string;
}

export interface ResumenPresupuesto {
  id: number;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  monto_limite: string | number;
  total_ingresos: string | number;
  total_gastos: string | number;
  saldo: string | number;
}

@Injectable({
  providedIn: 'root'
})
export class Presupuestos {
  private http = inject(HttpClient);
  private apiUrl = '/api/presupuestos/';

  listar(): Observable<Presupuesto[]> {
    return this.http.get<Presupuesto[]>(this.apiUrl);
  }

  crear(datos: {
    nombre: string;
    fecha_inicio: string;
    fecha_fin: string;
    monto_limite: number;
  }): Observable<Presupuesto> {
    return this.http.post<Presupuesto>(this.apiUrl, datos);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  resumen(): Observable<ResumenPresupuesto[]> {
    return this.http.get<ResumenPresupuesto[]>(
      `${this.apiUrl}resumen/`
    );
  }
}
