import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Resumen {
  total_ingresos: number;
  total_gastos: number;
  balance: number;
  cantidad_ingresos: number;
  cantidad_gastos: number;
}

@Injectable({
  providedIn: 'root'
})
export class ResumenService {
  private http = inject(HttpClient);

  obtener(): Observable<Resumen> {
    return this.http.get<Resumen>('/api/resumen/');
  }
}