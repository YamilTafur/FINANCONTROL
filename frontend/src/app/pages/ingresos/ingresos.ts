
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Ingresos as IngresosService, Ingreso } from '../../services/ingresos';
import { Categorias as CategoriasService, Categoria } from '../../services/categorias';
import { Presupuestos as PresupuestosService, Presupuesto } from '../../services/presupuestos';

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

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarPresupuestos();
    this.cargarIngresos();
  }

  nombreCategoria(id: number): string {
    return this.categorias.find(c => c.id === id)?.nombre ?? 'Sin categoría';
  }

  cargarCategorias(): void {
    this.categoriasServicio.listar().subscribe({
      next: datos => {
        this.categorias = datos.filter(
          c => c.tipo === 'INGRESO' && c.activa
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
        this.error = respuesta.error?.detail
          || 'No se pudo registrar el ingreso.';
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
}
