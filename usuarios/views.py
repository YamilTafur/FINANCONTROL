
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistroUsuarioForm


def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        formulario = RegistroUsuarioForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            messages.success(request, "Tu cuenta fue creada correctamente.")
            return redirect("inicio")
    else:
        formulario = RegistroUsuarioForm()

    return render(
        request,
        "usuarios/registro.html",
        {"formulario": formulario}
    )


@login_required
def inicio(request):
    return render(request, "usuarios/inicio.html")
