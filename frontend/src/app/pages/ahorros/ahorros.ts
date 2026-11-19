
import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import {
  Ahorros as AhorrosService,
  MetaAhorro,
  AporteAhorro,
  ConfiguracionProteccion,
  RetiroAhorro
} from '../../services/ahorros';

@Component({
  selector: 'app-ahorros',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './ahorros.html',
  styleUrl: './ahorros.css'
})
export class Ahorros implements OnInit {

  private servicio = inject(AhorrosService);
  private cdr = inject(ChangeDetectorRef);

  metas: MetaAhorro[] = [];
  aportes: AporteAhorro[] = [];
  protecciones: ConfiguracionProteccion[] = [];
  retiros: RetiroAhorro[] = [];

  metaSeleccionadaId: number | null = null;

  nombre = '';
  descripcionMeta = '';
  montoObjetivo: number | null = null;
  fechaInicio = new Date().toISOString().slice(0, 10);
  fechaLimite = '';

  montoAporte: number | null = null;
  fechaAporte = new Date().toISOString().slice(0, 10);
  descripcionAporte = '';

  montoRetiro: number | null = null;
  fechaRetiro = new Date().toISOString().slice(0, 10);
  descripcionRetiro = '';

  proteccionActiva = true;
  permitirRetiros = false;
  requiereConfirmacion = true;
  montoMinimoProtegido = 0;

  cargando = false;
  guardandoProteccion = false;

  mensaje = '';
  error = '';

  ngOnInit(): void {
    this.cargarDatos();
  }

  get metaSeleccionada(): MetaAhorro | undefined {
    return this.metas.find(
      meta => meta.id === this.metaSeleccionadaId
    );
  }

  get totalAhorrado(): number {
    return this.metas.reduce(
      (total, meta) => total + Number(meta.total_ahorrado),
      0
    );
  }

  get retirosPendientes(): number {
    return this.retiros.filter(
      retiro => retiro.estado === 'PENDIENTE'
    ).length;
  }

  get proteccionSeleccionada(): ConfiguracionProteccion | undefined {
    return this.protecciones.find(
      proteccion => proteccion.meta === this.metaSeleccionadaId
    );
  }

  private obtenerMensajeError(
    respuesta: any,
    mensajePredeterminado: string
  ): string {
    const datos = respuesta?.error;

    if (typeof datos === 'string') {
      return datos;
    }

    if (datos?.detail) {
      return datos.detail;
    }

    if (datos?.message) {
      return datos.message;
    }

    if (datos && typeof datos === 'object') {
      for (const [campo, valor] of Object.entries(datos)) {
        if (Array.isArray(valor) && valor.length > 0) {
          return `${campo}: ${valor[0]}`;
        }

        if (typeof valor === 'string' && valor) {
          return `${campo}: ${valor}`;
        }
      }
    }

    return mensajePredeterminado;
  }

  cargarDatos(): void {
    this.cargando = true;
    this.error = '';

    this.servicio.listarMetas().subscribe({
      next: datos => {
        this.metas = datos;

        if (
          !this.metaSeleccionadaId ||
          !this.metas.some(
            meta => meta.id === this.metaSeleccionadaId
          )
        ) {
          this.metaSeleccionadaId = this.metas[0]?.id ?? null;
        }

        this.cargarAportes();
        this.cargarProtecciones();
        this.cargarRetiros();

        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudieron cargar las metas de ahorro.'
        );

        this.cargando = false;
        this.cdr.markForCheck();
      }
    });
  }

  cargarAportes(): void {
    this.servicio.listarAportes().subscribe({
      next: datos => {
        this.aportes = datos;
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudieron cargar los aportes.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  cargarProtecciones(): void {
    this.servicio.listarProtecciones().subscribe({
      next: datos => {
        this.protecciones = datos;
        this.cargarFormularioProteccion();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo consultar la protección de las metas.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  cargarRetiros(): void {
    this.servicio.listarRetiros().subscribe({
      next: datos => {
        this.retiros = datos;
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudieron cargar las solicitudes de retiro.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  cambiarMeta(): void {
    this.limpiarMensajes();
    this.cargarFormularioProteccion();
  }

  cargarFormularioProteccion(): void {
    const proteccion = this.proteccionSeleccionada;

    this.proteccionActiva =
      proteccion?.proteccion_activa ?? true;

    this.permitirRetiros =
      proteccion?.permitir_retiros ?? false;

    this.requiereConfirmacion =
      proteccion?.requiere_confirmacion ?? true;

    this.montoMinimoProtegido = Number(
      proteccion?.monto_minimo_protegido ?? 0
    );
  }

  crearMeta(): void {
    this.limpiarMensajes();

    if (
      !this.nombre.trim() ||
      !this.montoObjetivo ||
      this.montoObjetivo <= 0 ||
      !this.fechaInicio
    ) {
      this.error = 'Completa el nombre, objetivo y fecha de inicio.';
      return;
    }

    if (
      this.fechaLimite &&
      this.fechaLimite < this.fechaInicio
    ) {
      this.error = 'La fecha límite no puede ser anterior al inicio.';
      return;
    }

    this.servicio.crearMeta({
      nombre: this.nombre.trim(),
      descripcion: this.descripcionMeta.trim(),
      monto_objetivo: this.montoObjetivo,
      fecha_inicio: this.fechaInicio,
      fecha_limite: this.fechaLimite || null
    }).subscribe({
      next: meta => {
        this.nombre = '';
        this.descripcionMeta = '';
        this.montoObjetivo = null;
        this.fechaLimite = '';

        this.metaSeleccionadaId = meta.id;
        this.mensaje = 'Meta de ahorro creada correctamente.';

        this.cargarDatos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo crear la meta.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  registrarAporte(): void {
    this.limpiarMensajes();

    if (
      !this.metaSeleccionadaId ||
      !this.montoAporte ||
      this.montoAporte <= 0 ||
      !this.fechaAporte
    ) {
      this.error = 'Selecciona una meta e ingresa un monto válido.';
      return;
    }

    this.servicio.crearAporte({
      meta: this.metaSeleccionadaId,
      monto: this.montoAporte,
      fecha: this.fechaAporte,
      descripcion: this.descripcionAporte.trim()
    }).subscribe({
      next: () => {
        this.montoAporte = null;
        this.descripcionAporte = '';

        this.mensaje = 'Aporte registrado correctamente.';

        this.cargarDatos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo registrar el aporte.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  guardarProteccion(): void {
    console.log('PRUEBA: se ejecutó guardarProteccion()');

    this.limpiarMensajes();

    if (this.guardandoProteccion) {
      return;
    }

    if (!this.metaSeleccionadaId) {
      this.error = 'Primero selecciona una meta de ahorro.';
      return;
    }

    if (
      !Number.isFinite(this.montoMinimoProtegido) ||
      this.montoMinimoProtegido < 0
    ) {
      this.error = 'El monto mínimo protegido no puede ser negativo.';
      return;
    }

    const datos = {
      proteccion_activa: this.proteccionActiva,
      permitir_retiros: this.permitirRetiros,
      requiere_confirmacion: this.requiereConfirmacion,
      monto_minimo_protegido: this.montoMinimoProtegido
    };

    const existente = this.proteccionSeleccionada;

    const solicitud = existente
      ? this.servicio.actualizarProteccion(
          existente.id,
          datos
        )
      : this.servicio.crearProteccion({
          meta: this.metaSeleccionadaId,
          ...datos
        });

    this.guardandoProteccion = true;
    this.cdr.markForCheck();

    solicitud.subscribe({
      next: configuracion => {
        this.guardandoProteccion = false;

        this.mensaje = '¡Configuración de protección guardada correctamente!';

        const indice = this.protecciones.findIndex(
          proteccion => proteccion.id === configuracion.id
        );

        if (indice >= 0) {
          this.protecciones[indice] = configuracion;
        } else {
          this.protecciones.push(configuracion);
        }

        this.cargarFormularioProteccion();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.guardandoProteccion = false;

        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo guardar la protección. Revisa los datos e inténtalo nuevamente.'
        );

        this.cdr.markForCheck();
      }
    });
  }

  solicitarRetiro(): void {
    this.limpiarMensajes();

    if (
      !this.metaSeleccionadaId ||
      !this.montoRetiro ||
      this.montoRetiro <= 0 ||
      !this.fechaRetiro
    ) {
      this.error = 'Selecciona una meta e ingresa un monto válido.';
      return;
    }

    this.servicio.crearRetiro({
      meta: this.metaSeleccionadaId,
      monto: this.montoRetiro,
      fecha: this.fechaRetiro,
      descripcion: this.descripcionRetiro.trim()
    }).subscribe({
      next: retiro => {
        this.montoRetiro = null;
        this.descripcionRetiro = '';

        this.mensaje = retiro.estado === 'PENDIENTE'
          ? 'Solicitud enviada. Está pendiente de confirmación.'
          : 'Retiro registrado correctamente.';

        this.cargarDatos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo solicitar el retiro.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  confirmarRetiro(id: number): void {
    if (!confirm('¿Confirmas este retiro de ahorro?')) {
      return;
    }

    this.servicio.confirmarRetiro(id).subscribe({
      next: () => {
        this.mensaje = 'Retiro confirmado correctamente.';
        this.cargarDatos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo confirmar el retiro.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  rechazarRetiro(id: number): void {
    if (!confirm('¿Deseas rechazar esta solicitud de retiro?')) {
      return;
    }

    this.servicio.rechazarRetiro(id).subscribe({
      next: () => {
        this.mensaje = 'Solicitud de retiro rechazada.';
        this.cargarDatos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = this.obtenerMensajeError(
          respuesta,
          'No se pudo rechazar el retiro.'
        );
        this.cdr.markForCheck();
      }
    });
  }

  nombreMeta(id: number): string {
    return this.metas.find(
      meta => meta.id === id
    )?.nombre ?? 'Meta';
  }

  limpiarMensajes(): void {
    this.mensaje = '';
    this.error = '';
  }
}
