
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MetaAhorro {
  id: number;
  nombre: string;
  descripcion: string;
  monto_objetivo: string;
  fecha_inicio: string;
  fecha_limite: string | null;
  estado: string;
  total_ahorrado: string;
  porcentaje_avance: string;
  monto_restante: string;
}

export interface AporteAhorro {
  id: number;
  meta: number;
  monto: string;
  fecha: string;
  descripcion: string;
}

export interface ConfiguracionProteccion {
  id: number;
  meta: number;
  proteccion_activa: boolean;
  permitir_retiros: boolean;
  requiere_confirmacion: boolean;
  monto_minimo_protegido: string | number;
}

export interface RetiroAhorro {
  id: number;
  meta: number;
  monto: string;
  fecha: string;
  descripcion: string;
  estado: 'PENDIENTE' | 'CONFIRMADO' | 'RECHAZADO';
  solicitado: string;
  resuelto: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class Ahorros {
  private http = inject(HttpClient);

  private metasUrl = '/api/ahorros/metas/';
  private aportesUrl = '/api/ahorros/aportes/';
  private proteccionesUrl = '/api/ahorros/protecciones/';
  private retirosUrl = '/api/ahorros/retiros/';

  listarMetas(): Observable<MetaAhorro[]> {
    return this.http.get<MetaAhorro[]>(this.metasUrl);
  }

  crearMeta(meta: {
    nombre: string;
    descripcion: string;
    monto_objetivo: number;
    fecha_inicio: string;
    fecha_limite: string | null;
  }): Observable<MetaAhorro> {
    return this.http.post<MetaAhorro>(this.metasUrl, meta);
  }

  listarAportes(): Observable<AporteAhorro[]> {
    return this.http.get<AporteAhorro[]>(this.aportesUrl);
  }

  crearAporte(aporte: {
    meta: number;
    monto: number;
    fecha: string;
    descripcion: string;
  }): Observable<AporteAhorro> {
    return this.http.post<AporteAhorro>(this.aportesUrl, aporte);
  }

  listarProtecciones(): Observable<ConfiguracionProteccion[]> {
    return this.http.get<ConfiguracionProteccion[]>(this.proteccionesUrl);
  }

  crearProteccion(configuracion: {
    meta: number;
    proteccion_activa: boolean;
    permitir_retiros: boolean;
    requiere_confirmacion: boolean;
    monto_minimo_protegido: string | number;
  }): Observable<ConfiguracionProteccion> {
    return this.http.post<ConfiguracionProteccion>(
      this.proteccionesUrl,
      configuracion
    );
  }

  actualizarProteccion(
    id: number,
    configuracion: Partial<ConfiguracionProteccion>
  ): Observable<ConfiguracionProteccion> {
    return this.http.patch<ConfiguracionProteccion>(
      `${this.proteccionesUrl}${id}/`,
      configuracion
    );
  }

  listarRetiros(): Observable<RetiroAhorro[]> {
    return this.http.get<RetiroAhorro[]>(this.retirosUrl);
  }

  crearRetiro(retiro: {
    meta: number;
    monto: number;
    fecha: string;
    descripcion: string;
  }): Observable<RetiroAhorro> {
    return this.http.post<RetiroAhorro>(this.retirosUrl, retiro);
  }

  confirmarRetiro(id: number): Observable<RetiroAhorro> {
    return this.http.post<RetiroAhorro>(
      `${this.retirosUrl}${id}/confirmar/`,
      {}
    );
  }

  rechazarRetiro(id: number): Observable<RetiroAhorro> {
    return this.http.post<RetiroAhorro>(
      `${this.retirosUrl}${id}/rechazar/`,
      {}
    );
  }
}
