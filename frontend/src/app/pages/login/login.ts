
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login implements OnInit {
  private auth = inject(Auth);
  private router = inject(Router);

  username = '';
  password = '';
  error = '';
  cargando = false;

  ngOnInit(): void {
    this.auth.obtenerCsrf().subscribe({
      error: () => {
        this.error = 'No se pudo conectar con el servidor.';
      }
    });
  }

  iniciarSesion(): void {
    this.error = '';
    this.cargando = true;

    this.auth.iniciarSesion(this.username, this.password).subscribe({
      next: () => {
        this.cargando = false;
        this.router.navigate(['/menu']);
      },
      error: (respuesta) => {
        this.cargando = false;
        this.error = respuesta.error?.error || 'No se pudo iniciar sesión.';
      }
    });
  }
}
