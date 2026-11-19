
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [RouterLink],
  template: `
    <main class="contenedor">
      <header>
        <h1>FINANCONTROL</h1>
        <p>Sistema de gestión financiera personal</p>
      </header>

      <section class="bienvenida">
        <h2>Menú principal</h2>
        <p>Selecciona el módulo que deseas administrar.</p>
        <a routerLink="/ahorros" class="tarjeta">
  <span class="icono">💰</span>
  <h3>Ahorros</h3>
  <p>Administra tus metas, aportes y protección de ahorros.</p>
</a>
      </section>

      <section class="modulos">
        <a routerLink="/panel" class="tarjeta">
          <span class="icono">📊</span>
          <h3>Panel principal</h3>
          <p>Consulta tu resumen financiero.</p>
        </a>

        <a routerLink="/categorias" class="tarjeta">
          <span class="icono">📁</span>
          <h3>Categorías</h3>
          <p>Administra tus categorías de ingresos y gastos.</p>
        </a>

        <a routerLink="/ingresos" class="tarjeta">
          <span class="icono">💰</span>
          <h3>Ingresos</h3>
          <p>Registra y consulta tus ingresos.</p>
        </a>

        <a routerLink="/gastos" class="tarjeta">
          <span class="icono">🧾</span>
          <h3>Gastos</h3>
          <p>Registra y consulta tus gastos.</p>
        </a>

        <a routerLink="/presupuestos" class="tarjeta">
          <span class="icono">📅</span>
          <h3>Presupuestos</h3>
          <p>Organiza tus presupuestos por periodos.</p>
        </a>
      </section>
    </main>
  `,
  styles: [`
    .contenedor {
      max-width: 1100px;
      margin: 40px auto;
      padding: 20px;
      font-family: Arial, sans-serif;
      color: #1f2937;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
    }

    header h1 {
      color: #166534;
      font-size: 32px;
      margin-bottom: 8px;
    }

    header p, .bienvenida p {
      color: #64748b;
    }

    .bienvenida {
      margin-bottom: 25px;
    }

    .modulos {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
    }

    .tarjeta {
      display: block;
      padding: 25px;
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      text-decoration: none;
      color: inherit;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .tarjeta:hover {
      transform: translateY(-4px);
      box-shadow: 0 5px 18px rgba(0, 0, 0, 0.10);
    }

    .icono {
      font-size: 32px;
    }

    .tarjeta h3 {
      margin-bottom: 8px;
      color: #166534;
    }

    .tarjeta p {
      margin-bottom: 0;
      color: #64748b;
      font-size: 14px;
    }
  `]
})
export class Menu {}
