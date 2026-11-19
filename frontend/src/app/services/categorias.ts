
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Categoria {
  id: number;
  nombre: string;
  tipo: 'INGRESO' | 'GASTO';
  descripcion: string | null;
  activa: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class Categorias {
  private http = inject(HttpClient);
  private apiUrl = '/api/categorias/';

  listar(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(this.apiUrl);
  }

  crear(categoria: {
    nombre: string;
    tipo: 'INGRESO' | 'GASTO';
    descripcion: string;
    activa: boolean;
  }): Observable<Categoria> {
    return this.http.post<Categoria>(this.apiUrl, categoria);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}
