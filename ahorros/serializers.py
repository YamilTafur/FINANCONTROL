
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from rest_framework import serializers

from .models import (
    MetaAhorro,
    AporteAhorro,
    ConfiguracionProteccion,
    RetiroAhorro,
)


class MetaAhorroSerializer(serializers.ModelSerializer):

    total_ahorrado = serializers.SerializerMethodField()
    porcentaje_avance = serializers.SerializerMethodField()
    monto_restante = serializers.SerializerMethodField()

    class Meta:
        model = MetaAhorro
        fields = [
            "id",
            "nombre",
            "descripcion",
            "monto_objetivo",
            "fecha_inicio",
            "fecha_limite",
            "estado",
            "total_ahorrado",
            "porcentaje_avance",
            "monto_restante",
            "creado",
        ]
        read_only_fields = [
            "id",
            "total_ahorrado",
            "porcentaje_avance",
            "monto_restante",
            "creado",
        ]

    def obtener_total(self, meta):

        total_aportes = meta.aportes.aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        total_distribuciones = meta.distribuciones.filter(
            destino="AHORRO"
        ).aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        total_retiros = meta.retiros.filter(
            estado="CONFIRMADO"
        ).aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")

        total = (
            total_aportes
            + total_distribuciones
            - total_retiros
        )

        return max(total, Decimal("0.00"))

    def get_total_ahorrado(self, obj):

        return self.obtener_total(obj).quantize(
            Decimal("0.01")
        )

    def get_porcentaje_avance(self, obj):

        total = self.obtener_total(obj)

        porcentaje = (
            total / obj.monto_objetivo
        ) * Decimal("100")

        return porcentaje.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    def get_monto_restante(self, obj):

        total = self.obtener_total(obj)

        restante = obj.monto_objetivo - total

        if restante < 0:
            restante = Decimal("0.00")

        return restante.quantize(Decimal("0.01"))

    def validate_monto_objetivo(self, valor):

        if valor <= 0:
            raise serializers.ValidationError(
                "El monto objetivo debe ser mayor que cero."
            )

        return valor

    def validate(self, attrs):

        fecha_inicio = attrs.get(
            "fecha_inicio",
            self.instance.fecha_inicio if self.instance else None
        )

        fecha_limite = attrs.get(
            "fecha_limite",
            self.instance.fecha_limite if self.instance else None
        )

        if fecha_limite and fecha_inicio and fecha_limite < fecha_inicio:
            raise serializers.ValidationError({
                "fecha_limite": (
                    "La fecha límite no puede ser anterior "
                    "a la fecha de inicio."
                )
            })

        return attrs


class AporteAhorroSerializer(serializers.ModelSerializer):

    meta = serializers.PrimaryKeyRelatedField(
        queryset=MetaAhorro.objects.none()
    )

    class Meta:
        model = AporteAhorro
        fields = [
            "id",
            "meta",
            "monto",
            "fecha",
            "descripcion",
            "creado",
        ]
        read_only_fields = ["id", "creado"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            self.fields["meta"].queryset = MetaAhorro.objects.filter(
                usuario=request.user,
                estado="ACTIVA"
            )

    def validate_monto(self, valor):

        if valor <= 0:
            raise serializers.ValidationError(
                "El aporte debe ser mayor que cero."
            )

        return valor

    def validate(self, attrs):

        meta = attrs.get(
            "meta",
            self.instance.meta if self.instance else None
        )

        fecha = attrs.get(
            "fecha",
            self.instance.fecha if self.instance else None
        )

        if meta and fecha and fecha < meta.fecha_inicio:
            raise serializers.ValidationError({
                "fecha": (
                    "La fecha del aporte no puede ser anterior "
                    "al inicio de la meta."
                )
            })

        return attrs


class ConfiguracionProteccionSerializer(serializers.ModelSerializer):

    meta = serializers.PrimaryKeyRelatedField(
        queryset=MetaAhorro.objects.none()
    )

    class Meta:
        model = ConfiguracionProteccion
        fields = [
            "id",
            "meta",
            "proteccion_activa",
            "permitir_retiros",
            "requiere_confirmacion",
            "monto_minimo_protegido",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            self.fields["meta"].queryset = MetaAhorro.objects.filter(
                usuario=request.user
            )

    def validate_monto_minimo_protegido(self, valor):

        if valor < 0:
            raise serializers.ValidationError(
                "El monto mínimo protegido no puede ser negativo."
            )

        return valor


class RetiroAhorroSerializer(serializers.ModelSerializer):

    meta = serializers.PrimaryKeyRelatedField(
        queryset=MetaAhorro.objects.none()
    )

    class Meta:
        model = RetiroAhorro
        fields = [
            "id",
            "meta",
            "monto",
            "fecha",
            "descripcion",
            "estado",
            "solicitado",
            "resuelto",
        ]
        read_only_fields = [
            "id",
            "estado",
            "solicitado",
            "resuelto",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            self.fields["meta"].queryset = MetaAhorro.objects.filter(
                usuario=request.user,
                estado="ACTIVA"
            )

    def validate_monto(self, valor):

        if valor <= 0:
            raise serializers.ValidationError(
                "El monto del retiro debe ser mayor que cero."
            )

        return valor

    def validate(self, attrs):

        meta = attrs.get(
            "meta",
            self.instance.meta if self.instance else None
        )

        fecha = attrs.get(
            "fecha",
            self.instance.fecha if self.instance else None
        )

        if meta and fecha and fecha < meta.fecha_inicio:
            raise serializers.ValidationError({
                "fecha": (
                    "La fecha del retiro no puede ser anterior "
                    "al inicio de la meta."
                )
            })

        return attrs
