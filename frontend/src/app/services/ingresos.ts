
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export type DestinoDistribucion =
  | 'NECESIDADES'
  | 'GUSTOS'
  | 'DEUDAS'
  | 'AHORRO'
  | 'INVERSION';

export interface Ingreso {
  id: number;
  categoria: number;
  presupuesto: number | null;
  monto: string;
  fecha: string;
  descripcion: string;
  creado: string;
  tiene_distribucion: boolean;
}

export interface DetalleDistribucion {
  destino: DestinoDistribucion;
  monto: string | number;
  porcentaje?: string | number | null;
}

export interface CategoriaDistribucion {
  id: number;
  nombre: string;
  grupo: string;
}

export interface MetaAhorroDistribucion {
  id: number;
  nombre: string;
  monto_objetivo: string | number;
}

export interface ConfiguracionDistribucion {
  porcentaje_necesidades: number;
  porcentaje_gustos: number;
  porcentaje_deudas: number;
  porcentaje_ahorro: number;
  porcentaje_inversion: number;
  actualizada?: string;
}

export interface VistaPreviaDistribucion {
  mensaje: string;
  ingreso: {
    id: number;
    monto: string | number;
    fecha: string;
    descripcion: string;
  };
  tipo: 'MANUAL' | 'AUTOMATICA';
  modalidad: 'NINGUNA' | 'PREDETERMINADA' | 'PERSONALIZADA';
  detalles: DetalleDistribucion[];
  total_ingreso: string | number;
  total_distribuido: string | number;
  pendiente: string | number;
  opciones: {
    categorias: Record<string, CategoriaDistribucion[]>;
    metas_ahorro: MetaAhorroDistribucion[];
    inversion: {
      nombre: string;
      requiere_categoria: boolean;
    };
  };
}

@Injectable({ providedIn: 'root' })
export class Ingresos {
  private http = inject(HttpClient);

  private apiUrl = '/api/ingresos/';
  private distribucionUrl = '/api/distribucion/';

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

  obtenerConfiguracion(): Observable<ConfiguracionDistribucion> {
    return this.http.get<ConfiguracionDistribucion>(
      `${this.distribucionUrl}configuracion/`
    );
  }

  guardarConfiguracion(
    configuracion: ConfiguracionDistribucion
  ): Observable<ConfiguracionDistribucion> {
    return this.http.patch<ConfiguracionDistribucion>(
      `${this.distribucionUrl}configuracion/`,
      configuracion
    );
  }

  previsualizar(datos: {
    ingreso: number;
    tipo: 'MANUAL' | 'AUTOMATICA';
    modalidad: 'NINGUNA' | 'PREDETERMINADA' | 'PERSONALIZADA';
    asignaciones?: Record<string, number>;
  }): Observable<VistaPreviaDistribucion> {
    return this.http.post<VistaPreviaDistribucion>(
      `${this.distribucionUrl}previsualizar/`,
      datos
    );
  }

  confirmar(datos: {
    ingreso: number;
    tipo: 'MANUAL' | 'AUTOMATICA';
    modalidad: 'NINGUNA' | 'PREDETERMINADA' | 'PERSONALIZADA';
    detalles: Array<{
      destino: DestinoDistribucion;
      categoria?: number;
      meta_ahorro?: number;
      monto: number;
      porcentaje?: number;
    }>;
  }): Observable<any> {
    return this.http.post(
      `${this.distribucionUrl}confirmar/`,
      datos
    );
  }
}
