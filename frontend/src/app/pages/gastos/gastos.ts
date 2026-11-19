
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Gastos as GastosService, Gasto } from '../../services/gastos';
import { Categorias as CategoriasService, Categoria } from '../../services/categorias';
import { Presupuestos as PresupuestosService, Presupuesto } from '../../services/presupuestos';

@Component({
  selector: 'app-gastos',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './gastos.html',
  styleUrl: './gastos.css'
})
export class Gastos implements OnInit {
  private servicio = inject(GastosService);
  private categoriasServicio = inject(CategoriasService);
  private presupuestosServicio = inject(PresupuestosService);
  private cdr = inject(ChangeDetectorRef);

  lista: Gasto[] = [];
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

  get totalGastos(): number {
    return this.lista.reduce((total, gasto) => total + Number(gasto.monto), 0);
  }

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarPresupuestos();
    this.cargarGastos();
  }

  cargarCategorias(): void {
    this.categoriasServicio.listar().subscribe({
      next: datos => {
        this.categorias = datos.filter(
          c => c.tipo === 'GASTO' && c.activa
        );
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

  cargarGastos(): void {
    this.cargando = true;

    this.servicio.listar().subscribe({
      next: datos => {
        this.lista = datos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.cargando = false;
        this.error = respuesta.status === 403
          ? 'Tu sesión no está autorizada. Vuelve a iniciar sesión.'
          : 'No se pudieron cargar los gastos.';
        this.cdr.markForCheck();
      }
    });
  }

  nombrePresupuesto(id: number | null): string {
    return this.presupuestos.find(p => p.id === id)?.nombre ?? 'Sin presupuesto';
  }

  registrarGasto(): void {
    this.error = '';
    this.mensaje = '';

    if (
      !this.categoria ||
      this.monto === null ||
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
        this.mensaje = 'Gasto registrado correctamente.';
        this.cargarGastos();
        this.cdr.markForCheck();
      },
      error: respuesta => {
        this.error = respuesta.error?.detail ||
          'No se pudo registrar el gasto.';
        this.cdr.markForCheck();
      }
    });
  }

  eliminarGasto(id: number): void {
    if (!confirm('¿Deseas eliminar este gasto?')) return;

    this.servicio.eliminar(id).subscribe({
      next: () => {
        this.mensaje = 'Gasto eliminado correctamente.';
        this.cargarGastos();
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No se pudo eliminar el gasto.';
        this.cdr.markForCheck();
      }
    });
  }

  nombreCategoria(id: number): string {
    return this.categorias.find(c => c.id === id)?.nombre ?? 'Sin categoría';
  }
}
