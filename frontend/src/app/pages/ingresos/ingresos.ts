
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  Ingresos as IngresosService,
  Ingreso,
  ConfiguracionDistribucion,
  VistaPreviaDistribucion,
  DestinoDistribucion
} from '../../services/ingresos';

import {
  Categorias as CategoriasService,
  Categoria
} from '../../services/categorias';

import {
  Presupuestos as PresupuestosService,
  Presupuesto
} from '../../services/presupuestos';

@Component({
  selector: 'app-ingresos',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './ingresos.html',
  styleUrl: './ingresos.css'
})
export class Ingresos implements OnInit {
  private servicio = inject(IngresosService);
  private categoriasServicio = inject(CategoriasService);
  private presupuestosServicio = inject(PresupuestosService);
  private cdr = inject(ChangeDetectorRef);

  lista: Ingreso[] = [];
  categorias: Categoria[] = [];
  presupuestos: Presupuesto[] = [];

  categoria = 0;
  presupuesto: number | null = null;
  monto: number | null = null;
  fecha = new Date().toISOString().slice(0, 10);
  descripcion = '';

  cargando = false;
  mensaje = '';
  error = '';

  configuracion: ConfiguracionDistribucion = {
    porcentaje_necesidades: 55,
    porcentaje_gustos: 5,
    porcentaje_deudas: 10,
    porcentaje_ahorro: 15,
    porcentaje_inversion: 15
  };

  guardandoConfiguracion = false;
  mostrarConfiguracion = false;

  ingresoSeleccionado: Ingreso | null = null;
  vistaPrevia: VistaPreviaDistribucion | null = null;

  tipoDistribucion: 'MANUAL' | 'AUTOMATICA' = 'AUTOMATICA';
  modalidad: 'NINGUNA' | 'PREDETERMINADA' | 'PERSONALIZADA' = 'PREDETERMINADA';

  manual: Record<DestinoDistribucion, number> = {
    NECESIDADES: 0,
    GUSTOS: 0,
    DEUDAS: 0,
    AHORRO: 0,
    INVERSION: 0
  };

  categoriasSeleccionadas: Record<string, number | null> = {
    NECESIDADES: null,
    GUSTOS: null,
    DEUDAS: null
  };

  metaSeleccionada: number | null = null;
  procesandoDistribucion = false;

  readonly destinos: DestinoDistribucion[] = [
    'NECESIDADES',
    'GUSTOS',
    'DEUDAS',
    'AHORRO',
    'INVERSION'
  ];

  readonly Number = Number;

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarPresupuestos();
    this.cargarIngresos();
    this.cargarConfiguracion();
  }

  nombreCategoria(id: number): string {
    return this.categorias.find(c => c.id === id)?.nombre ?? 'Sin categoría';
  }

  cargarCategorias(): void {
    this.categoriasServicio.listar().subscribe({
      next: datos => {
        this.categorias = datos.filter(c => c.tipo === 'INGRESO' && c.activa);
        this.categoria = this.categorias[0]?.id ?? 0;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudieron cargar las categorías.';
        this.cdr.markForCheck();
      }
    });
  }

  cargarPresupuestos(): void {
    this.presupuestosServicio.listar().subscribe({
      next: datos => {
        this.presupuestos = datos;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudieron cargar los presupuestos.';
        this.cdr.markForCheck();
      }
    });
  }

  cargarIngresos(): void {
    this.cargando = true;

    this.servicio.listar().subscribe({
      next: datos => {
        this.lista = datos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.cargando = false;
        this.error = 'No se pudieron cargar los ingresos.';
        this.cdr.markForCheck();
      }
    });
  }

  cargarConfiguracion(): void {
    this.servicio.obtenerConfiguracion().subscribe({
      next: datos => {
        this.configuracion = datos;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudo cargar la configuración de distribución.';
        this.cdr.markForCheck();
      }
    });
  }

  registrarIngreso(): void {
    this.error = '';
    this.mensaje = '';

    if (
      !this.categoria ||
      !this.monto ||
      this.monto <= 0 ||
      !this.fecha ||
      !this.descripcion.trim()
    ) {
      this.error = 'Completa todos los campos con valores válidos.';
      return;
    }

    this.servicio.crear({
      categoria: this.categoria,
      presupuesto: this.presupuesto,
      monto: this.monto,
      fecha: this.fecha,
      descripcion: this.descripcion.trim()
    }).subscribe({
      next: () => {
        this.monto = null;
        this.descripcion = '';
        this.presupuesto = null;
        this.mensaje = 'Ingreso registrado correctamente.';
        this.cargarIngresos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = respuesta.error?.detail || 'No se pudo registrar el ingreso.';
        this.cdr.markForCheck();
      }
    });
  }

  eliminarIngreso(id: number): void {
    if (!confirm('¿Deseas eliminar este ingreso?')) return;

    this.servicio.eliminar(id).subscribe({
      next: () => {
        this.mensaje = 'Ingreso eliminado correctamente.';
        this.cargarIngresos();
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudo eliminar el ingreso.';
        this.cdr.markForCheck();
      }
    });
  }

  guardarConfiguracion(): void {
    const valores = [
      this.configuracion.porcentaje_necesidades,
      this.configuracion.porcentaje_gustos,
      this.configuracion.porcentaje_deudas,
      this.configuracion.porcentaje_ahorro,
      this.configuracion.porcentaje_inversion
    ];

    if (valores.some(v => v < 0 || v > 100)) {
      this.error = 'Cada porcentaje debe estar entre 0 y 100.';
      return;
    }

    if (valores.reduce((a, b) => Number(a) + Number(b), 0) !== 100) {
      this.error = 'Los porcentajes deben sumar exactamente 100%.';
      return;
    }

    this.error = '';
    this.mensaje = '';
    this.guardandoConfiguracion = true;

    this.servicio.guardarConfiguracion(this.configuracion).subscribe({
      next: datos => {
        this.configuracion = datos;
        this.guardandoConfiguracion = false;
        this.mensaje = 'Configuración de distribución guardada.';
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.guardandoConfiguracion = false;
        this.error = respuesta.error?.detail || 'No se pudo guardar la configuración.';
        this.cdr.markForCheck();
      }
    });
  }

  abrirDistribucion(ingreso: Ingreso): void {
    this.error = '';
    this.mensaje = '';
    this.vistaPrevia = null;
    this.ingresoSeleccionado = ingreso;

    this.manual = {
      NECESIDADES: 0,
      GUSTOS: 0,
      DEUDAS: 0,
      AHORRO: 0,
      INVERSION: 0
    };

    this.categoriasSeleccionadas = {
      NECESIDADES: null,
      GUSTOS: null,
      DEUDAS: null
    };

    this.metaSeleccionada = null;
    this.tipoDistribucion = 'AUTOMATICA';
    this.modalidad = 'PREDETERMINADA';
    this.cdr.markForCheck();
  }

  previsualizarAutomatica(
    modalidad: 'PREDETERMINADA' | 'PERSONALIZADA'
  ): void {
    this.tipoDistribucion = 'AUTOMATICA';
    this.modalidad = modalidad;

    this.enviarPrevisualizacion({
      ingreso: this.ingresoSeleccionado!.id,
      tipo: 'AUTOMATICA',
      modalidad
    });
  }

  previsualizarManual(): void {
    if (!this.ingresoSeleccionado) return;

    const asignaciones: Record<string, number> = {};

    for (const destino of this.destinos) {
      const valor = Number(this.manual[destino]);

      if (!Number.isFinite(valor) || valor < 0) {
        this.error = 'Los montos manuales deben ser valores positivos o cero.';
        return;
      }

      if (valor > 0) {
        asignaciones[destino] = valor;
      }
    }

    if (Object.keys(asignaciones).length === 0) {
      this.error = 'Ingresa al menos un monto para distribuir.';
      return;
    }

    this.tipoDistribucion = 'MANUAL';
    this.modalidad = 'NINGUNA';

    this.enviarPrevisualizacion({
      ingreso: this.ingresoSeleccionado.id,
      tipo: 'MANUAL',
      modalidad: 'NINGUNA',
      asignaciones
    });
  }

  private enviarPrevisualizacion(datos: {
    ingreso: number;
    tipo: 'MANUAL' | 'AUTOMATICA';
    modalidad: 'NINGUNA' | 'PREDETERMINADA' | 'PERSONALIZADA';
    asignaciones?: Record<string, number>;
  }): void {
    this.error = '';
    this.mensaje = '';
    this.vistaPrevia = null;
    this.procesandoDistribucion = true;

    this.servicio.previsualizar(datos).subscribe({
      next: resultado => {
        this.vistaPrevia = resultado;
        this.procesandoDistribucion = false;
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.procesandoDistribucion = false;
        this.error = this.obtenerError(respuesta);
        this.cdr.markForCheck();
      }
    });
  }

  categoriasDestino(destino: string) {
    return this.vistaPrevia?.opciones.categorias[destino] ?? [];
  }

  confirmarDistribucion(): void {
    if (!this.vistaPrevia || !this.ingresoSeleccionado) return;

    const detalles = [];

    for (const detalle of this.vistaPrevia.detalles) {
      const montoDetalle = Number(detalle.monto);

      if (montoDetalle <= 0) continue;

      const item: {
        destino: DestinoDistribucion;
        categoria?: number;
        meta_ahorro?: number;
        monto: number;
        porcentaje?: number;
      } = {
        destino: detalle.destino,
        monto: montoDetalle
      };

      if (detalle.destino === 'NECESIDADES' ||
          detalle.destino === 'GUSTOS' ||
          detalle.destino === 'DEUDAS') {
        const categoria = this.categoriasSeleccionadas[detalle.destino];

        if (!categoria) {
          this.error = `Selecciona una categoría para ${detalle.destino.toLowerCase()}.`;
          return;
        }

        item.categoria = categoria;
      }

      if (detalle.destino === 'AHORRO' && this.metaSeleccionada) {
        item.meta_ahorro = this.metaSeleccionada;
      }

      if (this.tipoDistribucion === 'AUTOMATICA') {
        item.porcentaje = Number(detalle.porcentaje);
      }

      detalles.push(item);
    }

    if (detalles.length === 0) {
      this.error = 'No hay montos para confirmar.';
      return;
    }

    this.error = '';
    this.mensaje = '';
    this.procesandoDistribucion = true;

    this.servicio.confirmar({
      ingreso: this.ingresoSeleccionado.id,
      tipo: this.tipoDistribucion,
      modalidad: this.modalidad,
      detalles
    }).subscribe({
      next: () => {
        this.procesandoDistribucion = false;
        this.mensaje = 'Distribución confirmada correctamente.';
        this.vistaPrevia = null;
        this.ingresoSeleccionado = null;
        this.cargarIngresos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.procesandoDistribucion = false;
        this.error = this.obtenerError(respuesta);
        this.cdr.markForCheck();
      }
    });
  }

  cancelarDistribucion(): void {
    this.ingresoSeleccionado = null;
    this.vistaPrevia = null;
    this.error = '';
    this.cdr.markForCheck();
  }

  private obtenerError(respuesta: any): string {
    const datos = respuesta.error;

    if (typeof datos === 'string') return datos;
    if (datos?.detail) return datos.detail;

    if (datos && typeof datos === 'object') {
      const clave = Object.keys(datos)[0];
      const valor = datos[clave];

      if (Array.isArray(valor)) return String(valor[0]);
      if (typeof valor === 'string') return valor;
    }

    return 'Ocurrió un error al procesar la distribución.';
  }
}
