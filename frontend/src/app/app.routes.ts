
import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Menu } from './pages/menu/menu';
import { Categorias } from './pages/categorias/categorias';
import { Ingresos } from './pages/ingresos/ingresos';
import { Gastos } from './pages/gastos/gastos';
import { Panel } from './pages/panel/panel';
import { PresupuestosComponent } from './pages/presupuestos/presupuestos';
import { Ahorros } from './pages/ahorros/ahorros';

export const routes: Routes = [
  {
    path: 'login',
    component: Login
  },
  {
    path: 'menu',
    component: Menu
  },
  {
    path: 'categorias',
    component: Categorias
  },
  {
    path: 'ingresos',
    component: Ingresos
  },
  {
    path: 'gastos',
    component: Gastos
  },
  {
    path: 'panel',
    component: Panel
  },
  {
    path: 'presupuestos',
    component: PresupuestosComponent
  },

  {
  path: 'ahorros',
  component: Ahorros
},

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];
