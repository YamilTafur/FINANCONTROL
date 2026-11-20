
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  Categorias as CategoriasService,
  Categoria,
  GrupoDistribucion
} from '../../services/categorias';

@Component({
  selector: 'app-categorias',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './categorias.html',
  styleUrl: './categorias.css'
})
export class Categorias implements OnInit {
  private servicio = inject(CategoriasService);
  private cdr = inject(ChangeDetectorRef);

  lista: Categoria[] = [];

  nombre = '';
  tipo: 'INGRESO' | 'GASTO' = 'GASTO';
  grupoDistribucion: GrupoDistribucion | null = 'NECESIDADES';
  descripcion = '';

  categoriaEditandoId: number | null = null;

  cargando = false;
  mensaje = '';
  error = '';

  ngOnInit(): void {
    this.cargarCategorias();
  }

  cargarCategorias(): void {
    this.cargando = true;
    this.error = '';

    this.servicio.listar().subscribe({
      next: (datos) => {
        this.lista = datos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (respuesta) => {
        this.cargando = false;
        this.error = respuesta.status === 403
          ? 'Tu sesión no está autorizada. Vuelve a iniciar sesión.'
          : 'No se pudieron cargar las categorías.';

        this.cdr.markForCheck();
      }
    });
  }

  cambiarTipo(): void {
    if (this.tipo === 'INGRESO') {
      this.grupoDistribucion = null;
    } else if (!this.grupoDistribucion) {
      this.grupoDistribucion = 'NECESIDADES';
    }
  }

  crearCategoria(): void {
    this.error = '';
    this.mensaje = '';

    if (!this.nombre.trim()) {
      this.error = 'Ingresa el nombre de la categoría.';
      return;
    }

    if (this.tipo === 'GASTO' && !this.grupoDistribucion) {
      this.error = 'Selecciona el grupo de distribución.';
      return;
    }

    const datos = {
      nombre: this.nombre.trim(),
      tipo: this.tipo,
      grupo_distribucion: this.tipo === 'GASTO'
        ? this.grupoDistribucion
        : null,
      descripcion: this.descripcion,
      activa: true
    };

    const solicitud = this.categoriaEditandoId !== null
      ? this.servicio.actualizar(this.categoriaEditandoId, datos)
      : this.servicio.crear(datos);

    solicitud.subscribe({
      next: () => {
        const estabaEditando = this.categoriaEditandoId !== null;

        this.limpiarFormulario();
        this.mensaje = estabaEditando
          ? 'Categoría actualizada correctamente.'
          : 'Categoría registrada correctamente.';

        this.cargarCategorias();
      },
      error: (respuesta) => {
        this.error = respuesta.status === 403
          ? 'No tienes autorización o falta el token CSRF.'
          : 'No se pudo guardar la categoría.';

        this.cdr.markForCheck();
      }
    });
  }

  editarCategoria(categoria: Categoria): void {
    this.error = '';
    this.mensaje = '';

    this.categoriaEditandoId = categoria.id;
    this.nombre = categoria.nombre;
    this.tipo = categoria.tipo;
    this.grupoDistribucion = categoria.grupo_distribucion;
    this.descripcion = categoria.descripcion || '';

    this.cambiarTipo();

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelarEdicion(): void {
    this.limpiarFormulario();
    this.error = '';
    this.mensaje = '';
  }

  private limpiarFormulario(): void {
    this.nombre = '';
    this.tipo = 'GASTO';
    this.grupoDistribucion = 'NECESIDADES';
    this.descripcion = '';
    this.categoriaEditandoId = null;
  }

  eliminarCategoria(id: number): void {
    if (!confirm('¿Deseas eliminar esta categoría?')) {
      return;
    }

    this.servicio.eliminar(id).subscribe({
      next: () => {
        this.mensaje = 'Categoría eliminada.';
        this.cargarCategorias();
      },
      error: () => {
        this.error = 'No se pudo eliminar la categoría.';
        this.cdr.markForCheck();
      }
    });
  }
}
