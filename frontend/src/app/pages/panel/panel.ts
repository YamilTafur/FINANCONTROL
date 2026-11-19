import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { ResumenService, Resumen } from '../../services/resumen';

@Component({
  selector: 'app-panel',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './panel.html',
  styleUrl: './panel.css'
})
export class Panel implements OnInit {
  private servicio = inject(ResumenService);
  private cdr = inject(ChangeDetectorRef);

  resumen: Resumen | null = null;
  cargando = false;
  error = '';

  ngOnInit(): void {
    this.cargarResumen();
  }

  cargarResumen(): void {
    this.cargando = true;
    this.error = '';

    this.servicio.obtener().subscribe({
      next: (datos) => {
        this.resumen = datos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (respuesta) => {
        this.cargando = false;
        this.error = respuesta.status === 403
          ? 'Tu sesión no está autorizada. Inicia sesión nuevamente.'
          : 'No se pudo cargar el resumen financiero.';
        this.cdr.markForCheck();
      }
    });
  }
}