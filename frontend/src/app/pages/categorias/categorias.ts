
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Categorias as CategoriasService, Categoria } from '../../services/categorias';

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
  descripcion = '';

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

  crearCategoria(): void {
    this.error = '';
    this.mensaje = '';

    if (!this.nombre.trim()) {
      this.error = 'Ingresa el nombre de la categoría.';
      return;
    }

    this.servicio.crear({
      nombre: this.nombre.trim(),
      tipo: this.tipo,
      descripcion: this.descripcion,
      activa: true
    }).subscribe({
      next: () => {
        this.nombre = '';
        this.descripcion = '';
        this.tipo = 'GASTO';
        this.mensaje = 'Categoría registrada correctamente.';
        this.cargarCategorias();
      },
      error: (respuesta) => {
        this.error = respuesta.status === 403
          ? 'No tienes autorización o falta el token CSRF.'
          : 'No se pudo registrar la categoría.';
      }
    });
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
      }
    });
  }
}
