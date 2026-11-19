
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CategoriaForm, IngresoForm, GastoForm
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    CategoriaSerializer,
    IngresoSerializer,
    GastoSerializer,
    PresupuestoSerializer,
    ConfiguracionDistribucionSerializer
)

from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Categoria,
    Ingreso,
    Gasto,
    Presupuesto,
    ConfiguracionDistribucion
)

from django.db import IntegrityError, transaction
from rest_framework import status

from .serializers import DistribucionConfirmacionSerializer

from .models import DistribucionIngreso, DetalleDistribucion

from .distribution_services import (
    calcular_distribucion_automatica,
    calcular_distribucion_manual,
    obtener_porcentajes_predeterminados,
)
from ahorros.models import MetaAhorro
from decimal import Decimal

@login_required
def panel_financiero(request):
    ingresos = Ingreso.objects.filter(usuario=request.user)
    gastos = Gasto.objects.filter(usuario=request.user)

    total_ingresos = sum(item.monto for item in ingresos)
    total_gastos = sum(item.monto for item in gastos)

    return render(request, "finanzas/panel.html", {
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": total_ingresos - total_gastos,
        "cantidad_ingresos": ingresos.count(),
        "cantidad_gastos": gastos.count(),
    })


@login_required
def lista_categorias(request):
    categorias = Categoria.objects.filter(
        usuario=request.user
    ).order_by("tipo", "nombre")

    return render(request, "finanzas/categorias.html", {
        "categorias": categorias
    })


@login_required
def crear_categoria(request):
    if request.method == "POST":
        formulario = CategoriaForm(request.POST)

        if formulario.is_valid():
            categoria = formulario.save(commit=False)
            categoria.usuario = request.user
            categoria.save()

            messages.success(request, "Categoría creada correctamente.")
            return redirect("lista_categorias")
    else:
        formulario = CategoriaForm()

    return render(request, "finanzas/formulario.html", {
        "formulario": formulario,
        "titulo": "Crear categoría",
    })


@login_required
def lista_ingresos(request):
    ingresos = Ingreso.objects.filter(
        usuario=request.user
    ).select_related("categoria", "presupuesto").order_by("-fecha")

    return render(request, "finanzas/ingresos.html", {
        "ingresos": ingresos
    })


@login_required
def crear_ingreso(request):
    if request.method == "POST":
        formulario = IngresoForm(request.POST, usuario=request.user)

        if formulario.is_valid():
            ingreso = formulario.save(commit=False)
            ingreso.usuario = request.user
            ingreso.save()

            messages.success(request, "Ingreso registrado correctamente.")
            return redirect("lista_ingresos")
    else:
        formulario = IngresoForm(usuario=request.user)

    return render(request, "finanzas/formulario.html", {
        "formulario": formulario,
        "titulo": "Registrar ingreso",
    })


@login_required
def lista_gastos(request):
    gastos = Gasto.objects.filter(
        usuario=request.user
    ).select_related("categoria", "presupuesto").order_by("-fecha")

    return render(request, "finanzas/gastos.html", {
        "gastos": gastos
    })


@login_required
def crear_gasto(request):
    if request.method == "POST":
        formulario = GastoForm(request.POST, usuario=request.user)

        if formulario.is_valid():
            gasto = formulario.save(commit=False)
            gasto.usuario = request.user
            gasto.save()

            messages.success(request, "Gasto registrado correctamente.")
            return redirect("lista_gastos")
    else:
        formulario = GastoForm(usuario=request.user)

    return render(request, "finanzas/formulario.html", {
        "formulario": formulario,
        "titulo": "Registrar gasto",
    })


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categoria.objects.filter(
            usuario=self.request.user
        ).order_by("nombre")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


from .serializers import IngresoSerializer


class IngresoViewSet(viewsets.ModelViewSet):
    serializer_class = IngresoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ingreso.objects.filter(
            usuario=self.request.user
        ).select_related(
            "categoria",
            "presupuesto"
        ).order_by("-fecha")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class GastoViewSet(viewsets.ModelViewSet):
    serializer_class = GastoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Gasto.objects.filter(
            usuario=self.request.user
        ).select_related(
            "categoria",
            "presupuesto"
        ).order_by("-fecha")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_api(request):
    usuario = request.user

    ingresos = Ingreso.objects.filter(usuario=usuario)
    gastos = Gasto.objects.filter(usuario=usuario)

    total_ingresos = ingresos.aggregate(
        total=Sum("monto")
    )["total"] or 0

    total_gastos = gastos.aggregate(
        total=Sum("monto")
    )["total"] or 0

    balance = total_ingresos - total_gastos

    return Response({
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": balance,
        "cantidad_ingresos": ingresos.count(),
        "cantidad_gastos": gastos.count(),
    })

class PresupuestoViewSet(viewsets.ModelViewSet):
    serializer_class = PresupuestoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Presupuesto.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_presupuestos_api(request):
    usuario = request.user
    presupuestos = Presupuesto.objects.filter(usuario=usuario)

    resultados = []

    for presupuesto in presupuestos:
        ingresos = Ingreso.objects.filter(
            usuario=usuario,
            presupuesto=presupuesto,
            fecha__gte=presupuesto.fecha_inicio,
            fecha__lte=presupuesto.fecha_fin
        ).aggregate(total=Sum("monto"))["total"] or 0

        gastos = Gasto.objects.filter(
            usuario=usuario,
            presupuesto=presupuesto,
            fecha__gte=presupuesto.fecha_inicio,
            fecha__lte=presupuesto.fecha_fin
        ).aggregate(total=Sum("monto"))["total"] or 0

        resultados.append({
    "id": presupuesto.id,
    "nombre": presupuesto.nombre,
    "fecha_inicio": presupuesto.fecha_inicio,
    "fecha_fin": presupuesto.fecha_fin,
    "monto_limite": presupuesto.monto_limite,
    "total_ingresos": ingresos,
    "total_gastos": gastos,
    "saldo": ingresos - gastos
})

    return Response(resultados)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def configuracion_distribucion_api(request):

    configuracion, creada = ConfiguracionDistribucion.objects.get_or_create(
        usuario=request.user
    )

    if request.method == "GET":
        serializer = ConfiguracionDistribucionSerializer(configuracion)
        return Response(serializer.data)

    serializer = ConfiguracionDistribucionSerializer(
        configuracion,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            "mensaje": "Configuración actualizada correctamente.",
            "configuracion": serializer.data
        })

    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def previsualizar_distribucion_api(request):

    ingreso_id = request.data.get("ingreso")
    tipo = request.data.get("tipo")
    modalidad = request.data.get("modalidad")

    # Comprobar que el ingreso pertenezca al usuario.
    try:
        ingreso = Ingreso.objects.get(
            id=ingreso_id,
            usuario=request.user
        )
    except (Ingreso.DoesNotExist, TypeError, ValueError):
        return Response(
            {"error": "El ingreso no existe o no pertenece a tu cuenta."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Evitar distribuir dos veces el mismo ingreso.
    if DistribucionIngreso.objects.filter(ingreso=ingreso).exists():
        return Response(
            {"error": "Este ingreso ya tiene una distribución registrada."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        if tipo == "MANUAL":

            if modalidad != "NINGUNA":
                return Response(
                    {"error": "La distribución manual debe utilizar la modalidad NINGUNA."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            resultado = calcular_distribucion_manual(
                ingreso.monto,
                request.data.get("asignaciones")
            )

        elif tipo == "AUTOMATICA":

            if modalidad == "PREDETERMINADA":

                porcentajes = obtener_porcentajes_predeterminados()

            elif modalidad == "PERSONALIZADA":

                configuracion, creada = (
                    ConfiguracionDistribucion.objects.get_or_create(
                        usuario=request.user
                    )
                )

                porcentajes = {
                    "NECESIDADES": configuracion.porcentaje_necesidades,
                    "GUSTOS": configuracion.porcentaje_gustos,
                    "DEUDAS": configuracion.porcentaje_deudas,
                    "AHORRO": configuracion.porcentaje_ahorro,
                    "INVERSION": configuracion.porcentaje_inversion,
                }

            else:
                return Response(
                    {"error": "Selecciona una modalidad automática válida."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            resultado = calcular_distribucion_automatica(
                ingreso.monto,
                porcentajes
            )

        else:
            return Response(
                {"error": "El tipo de distribución no es válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener categorías disponibles para cada destino.
        categorias = Categoria.objects.filter(
            usuario=request.user,
            tipo="GASTO",
            activa=True,
            grupo_distribucion__in=[
                "NECESIDADES",
                "GUSTOS",
                "DEUDAS"
            ]
        ).order_by("nombre")

        opciones_categorias = {
            "NECESIDADES": [],
            "GUSTOS": [],
            "DEUDAS": []
        }

        for categoria in categorias:
            opciones_categorias[categoria.grupo_distribucion].append({
                "id": categoria.id,
                "nombre": categoria.nombre,
                "grupo": categoria.grupo_distribucion
            })

        # Obtener metas de ahorro activas del usuario.
        metas = MetaAhorro.objects.filter(
            usuario=request.user,
            estado="ACTIVA"
        ).order_by("nombre")

        opciones_metas = [
            {
                "id": meta.id,
                "nombre": meta.nombre,
                "monto_objetivo": meta.monto_objetivo
            }
            for meta in metas
        ]

        return Response({
            "mensaje": "Propuesta de distribución calculada correctamente.",
            "ingreso": {
                "id": ingreso.id,
                "monto": ingreso.monto,
                "fecha": ingreso.fecha,
                "descripcion": ingreso.descripcion,
            },
            "tipo": tipo,
            "modalidad": modalidad,
            "detalles": resultado["detalles"],
            "total_ingreso": resultado["total_ingreso"],
            "total_distribuido": resultado["total_distribuido"],
            "pendiente": resultado["pendiente"],
            "opciones": {
                "categorias": opciones_categorias,
                "metas_ahorro": opciones_metas,
                "inversion": {
                    "nombre": "Reserva de inversión",
                    "requiere_categoria": False
                }
            }
        })

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirmar_distribucion_api(request):

    serializer = DistribucionConfirmacionSerializer(
        data=request.data,
        context={"request": request}
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    datos = serializer.validated_data

    try:
        with transaction.atomic():

            # Bloquear el ingreso durante la confirmación.
            ingreso = Ingreso.objects.select_for_update().get(
                id=datos["ingreso"].id,
                usuario=request.user
            )

            # Comprobar nuevamente que no esté distribuido.
            if DistribucionIngreso.objects.filter(
                ingreso=ingreso
            ).exists():
                return Response(
                    {"error": "Este ingreso ya tiene una distribución registrada."},
                    status=status.HTTP_409_CONFLICT
                )

            distribucion = DistribucionIngreso.objects.create(
                ingreso=ingreso,
                tipo=datos["tipo"],
                modalidad=datos["modalidad"]
            )

            detalles_guardados = []

            for detalle in datos["detalles"]:

                detalle_guardado = DetalleDistribucion.objects.create(
                    distribucion=distribucion,
                    destino=detalle["destino"],
                    categoria=detalle.get("categoria"),
                    meta_ahorro=detalle.get("meta_ahorro"),
                    monto=detalle["monto"],
                    porcentaje=detalle.get("porcentaje")
                )

                detalles_guardados.append({
                    "id": detalle_guardado.id,
                    "destino": detalle_guardado.destino,
                    "categoria": detalle_guardado.categoria_id,
                    "meta_ahorro": detalle_guardado.meta_ahorro_id,
                    "monto": detalle_guardado.monto,
                    "porcentaje": detalle_guardado.porcentaje,
                })

            total_distribuido = sum(
                (detalle["monto"] for detalle in datos["detalles"]),
                Decimal("0.00")
            )

            pendiente = ingreso.monto - total_distribuido

        return Response({
            "mensaje": "Distribución confirmada correctamente.",
            "distribucion": distribucion.id,
            "ingreso": ingreso.id,
            "tipo": distribucion.tipo,
            "modalidad": distribucion.modalidad,
            "detalles": detalles_guardados,
            "total_ingreso": ingreso.monto,
            "total_distribuido": total_distribuido,
            "pendiente": pendiente,
        }, status=status.HTTP_201_CREATED)

    except Ingreso.DoesNotExist:
        return Response(
            {"error": "El ingreso ya no existe o no pertenece a tu cuenta."},
            status=status.HTTP_404_NOT_FOUND
        )

    except IntegrityError:
        return Response(
            {
                "error": (
                    "Este ingreso ya tiene una distribucion registrada "
                    "o existe un conflicto al guardar los detalles."
                )
            },
            status=status.HTTP_409_CONFLICT
        )