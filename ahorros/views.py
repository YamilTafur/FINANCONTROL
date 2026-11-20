
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    MetaAhorro,
    AporteAhorro,
    ConfiguracionProteccion,
    RetiroAhorro,
)

from .serializers import (
    MetaAhorroSerializer,
    AporteAhorroSerializer,
    ConfiguracionProteccionSerializer,
    RetiroAhorroSerializer,
)


class MetaAhorroViewSet(viewsets.ModelViewSet):

    serializer_class = MetaAhorroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MetaAhorro.objects.filter(
            usuario=self.request.user
        ).order_by("-creado")

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class AporteAhorroViewSet(viewsets.ModelViewSet):

    serializer_class = AporteAhorroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AporteAhorro.objects.filter(
            meta__usuario=self.request.user
        ).select_related("meta").order_by("-fecha", "-creado")


class ConfiguracionProteccionViewSet(viewsets.ModelViewSet):

    serializer_class = ConfiguracionProteccionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConfiguracionProteccion.objects.filter(
            meta__usuario=self.request.user
        ).select_related("meta")

    def perform_create(self, serializer):

        meta = serializer.validated_data["meta"]

        if ConfiguracionProteccion.objects.filter(meta=meta).exists():
            raise ValidationError({
                "meta": (
                    "Esta meta ya tiene una configuración "
                    "de protección."
                )
            })

        serializer.save()


class RetiroAhorroViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = RetiroAhorroSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RetiroAhorro.objects.filter(
            meta__usuario=self.request.user
        ).select_related(
            "meta"
        ).order_by("-solicitado")

    def obtener_saldo_disponible(
        self,
        meta,
        excluir_retiro_id=None
    ):

        aportes = meta.aportes.aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        distribuciones = meta.distribuciones.filter(
            destino="AHORRO"
        ).aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        retiros_confirmados = meta.retiros.filter(
            estado="CONFIRMADO"
        ).aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        pendientes = meta.retiros.filter(
            estado="PENDIENTE"
        )

        if excluir_retiro_id is not None:
            pendientes = pendientes.exclude(
                id=excluir_retiro_id
            )

        total_pendiente = pendientes.aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        return (
            aportes
            + distribuciones
            - retiros_confirmados
            - total_pendiente
        )

    def perform_create(self, serializer):

        meta_original = serializer.validated_data["meta"]

        with transaction.atomic():

            meta = MetaAhorro.objects.select_for_update().get(
                id=meta_original.id,
                usuario=self.request.user
            )

            monto = serializer.validated_data["monto"]

            if meta.estado != "ACTIVA":
                raise ValidationError({
                    "meta": (
                        "Solo puedes retirar dinero "
                        "de metas activas."
                    )
                })

            saldo = self.obtener_saldo_disponible(meta)

            proteccion = ConfiguracionProteccion.objects.filter(
                meta=meta
            ).first()

            estado = "CONFIRMADO"
            resuelto = timezone.now()

            if proteccion and proteccion.proteccion_activa:

                if not proteccion.permitir_retiros:
                    raise ValidationError({
                        "retiro": (
                            "Los retiros están deshabilitados "
                            "por la configuración de protección."
                        )
                    })

                saldo_minimo = proteccion.monto_minimo_protegido

                if saldo - monto < saldo_minimo:
                    raise ValidationError({
                        "monto": (
                            "El retiro superaría el monto mínimo "
                            "protegido de la meta."
                        )
                    })

                if proteccion.requiere_confirmacion:
                    estado = "PENDIENTE"
                    resuelto = None

            if monto > saldo:
                raise ValidationError({
                    "monto": "El retiro supera el saldo disponible."
                })

            serializer.save(
                meta=meta,
                estado=estado,
                resuelto=resuelto
            )

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):

        with transaction.atomic():

            retiro = self.get_object()

            retiro = RetiroAhorro.objects.select_for_update().get(
                id=retiro.id
            )

            if retiro.estado != "PENDIENTE":
                raise ValidationError({
                    "retiro": "Esta solicitud ya fue resuelta."
                })

            meta = MetaAhorro.objects.select_for_update().get(
                id=retiro.meta_id,
                usuario=request.user
            )

            if meta.estado != "ACTIVA":
                raise ValidationError({
                    "meta": "La meta ya no está activa."
                })

            proteccion = ConfiguracionProteccion.objects.filter(
                meta=meta
            ).first()

            if proteccion and proteccion.proteccion_activa:

                if not proteccion.permitir_retiros:
                    raise ValidationError({
                        "retiro": (
                            "La protección actualmente "
                            "no permite retiros."
                        )
                    })

                saldo_minimo = proteccion.monto_minimo_protegido

            else:
                saldo_minimo = Decimal("0.00")

            saldo = self.obtener_saldo_disponible(
                meta,
                excluir_retiro_id=retiro.id
            )

            if saldo - retiro.monto < saldo_minimo:
                raise ValidationError({
                    "monto": (
                        "No se puede confirmar el retiro porque "
                        "se vulneraría el saldo disponible o protegido."
                    )
                })

            retiro.estado = "CONFIRMADO"
            retiro.resuelto = timezone.now()
            retiro.save(update_fields=["estado", "resuelto"])

        return Response(
            self.get_serializer(retiro).data
        )

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):

        with transaction.atomic():

            retiro = self.get_object()

            retiro = RetiroAhorro.objects.select_for_update().get(
                id=retiro.id
            )

            if retiro.estado != "PENDIENTE":
                raise ValidationError({
                    "retiro": "Esta solicitud ya fue resuelta."
                })

            retiro.estado = "RECHAZADO"
            retiro.resuelto = timezone.now()
            retiro.save(update_fields=["estado", "resuelto"])

        return Response(
            self.get_serializer(retiro).data
        )


@login_required
def resumen_ahorros_api(request):

    from finanzas.models import DetalleDistribucion

    ahorro_general = DetalleDistribucion.objects.filter(
        distribucion__ingreso__usuario=request.user,
        destino="AHORRO",
        meta_ahorro__isnull=True
    ).aggregate(
        total=Sum("monto")
    )["total"] or Decimal("0.00")

    return JsonResponse({
        "ahorro_general": str(ahorro_general)
    })
