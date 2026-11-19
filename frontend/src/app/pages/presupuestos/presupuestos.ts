
import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  Presupuestos,
  Presupuesto,
  ResumenPresupuesto
} from '../../services/presupuestos';

@Component({
  selector: 'app-presupuestos',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './presupuestos.html',
  styleUrl: './presupuestos.css'
})
export class PresupuestosComponent implements OnInit {
  private servicio = inject(Presupuestos);
  private cdr = inject(ChangeDetectorRef);

  lista: Presupuesto[] = [];
  resumenes: ResumenPresupuesto[] = [];

  nombre = '';
  fechaInicio = '';
  fechaFin = '';
  montoLimite: number | null = null;

  error = '';
  mensaje = '';
  cargando = false;

  ngOnInit(): void {
    this.listar();
    this.cargarResumen();
  }

  listar(): void {
    this.cargando = true;

    this.servicio.listar().subscribe({
      next: datos => {
        this.lista = datos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudieron cargar los presupuestos.';
        this.cargando = false;
        this.cdr.markForCheck();
      }
    });
  }

  cargarResumen(): void {
    this.servicio.resumen().subscribe({
      next: datos => {
        this.resumenes = datos;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudo cargar el resumen de presupuestos.';
        this.cdr.markForCheck();
      }
    });
  }

  obtenerResumen(id: number): ResumenPresupuesto | undefined {
    return this.resumenes.find(r => r.id === id);
  }

  formatearMonto(valor: string | number): string {
    return Number(valor).toFixed(2);
  }

  crear(): void {
    this.error = '';
    this.mensaje = '';

    if (
      !this.nombre.trim() ||
      !this.fechaInicio ||
      !this.fechaFin ||
      this.montoLimite === null
    ) {
      this.error = 'Completa todos los campos.';
      return;
    }

    if (this.fechaFin < this.fechaInicio) {
      this.error = 'La fecha final no puede ser anterior a la inicial.';
      return;
    }

    if (this.montoLimite <= 0) {
      this.error = 'El límite de gasto debe ser mayor que cero.';
      return;
    }

    this.servicio.crear({
      nombre: this.nombre.trim(),
      fecha_inicio: this.fechaInicio,
      fecha_fin: this.fechaFin,
      monto_limite: this.montoLimite
    }).subscribe({
      next: () => {
        this.nombre = '';
        this.fechaInicio = '';
        this.fechaFin = '';
        this.montoLimite = null;

        this.mensaje = 'Presupuesto creado correctamente.';

        this.listar();
        this.cargarResumen();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = respuesta.error?.nombre?.[0]
          || respuesta.error?.fecha_inicio?.[0]
          || respuesta.error?.monto_limite?.[0]
          || 'No se pudo crear el presupuesto.';

        this.cdr.markForCheck();
      }
    });
  }

  eliminar(id: number): void {
    if (!confirm('¿Deseas eliminar este presupuesto?')) return;

    this.servicio.eliminar(id).subscribe({
      next: () => {
        this.mensaje = 'Presupuesto eliminado.';
        this.listar();
        this.cargarResumen();
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudo eliminar el presupuesto.';
        this.cdr.markForCheck();
      }
    });
  }
}
