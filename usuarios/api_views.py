
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required


@require_GET
@ensure_csrf_cookie
def obtener_csrf(request):
    return JsonResponse({"mensaje": "CSRF listo"})


@require_POST
@csrf_protect
def iniciar_sesion_api(request):
    try:
        datos = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Datos inválidos"},
            status=400
        )

    usuario = authenticate(
        request,
        username=datos.get("username"),
        password=datos.get("password")
    )

    if usuario is None:
        return JsonResponse(
            {"error": "Usuario o contraseña incorrectos"},
            status=401
        )

    login(request, usuario)

    return JsonResponse({
        "mensaje": "Sesión iniciada",
        "usuario": usuario.username
    })


@require_POST
@login_required
def cerrar_sesion_api(request):
    logout(request)
    return JsonResponse({"mensaje": "Sesión cerrada"})
