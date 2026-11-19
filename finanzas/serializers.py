
from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from .models import (
    Categoria,
    Ingreso,
    Presupuesto,
    Gasto,
    ConfiguracionDistribucion,
    DistribucionIngreso,
    DetalleDistribucion,
)
from .distribution_services import (
    calcular_distribucion_automatica,
    obtener_porcentajes_predeterminados,
)

from ahorros.models import MetaAhorro


class CategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categoria
        fields = [
            "id",
            "nombre",
            "tipo",
            "grupo_distribucion",
            "descripcion",
            "activa",
        ]


class IngresoSerializer(serializers.ModelSerializer):

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.none()
    )

    presupuesto = serializers.PrimaryKeyRelatedField(
        queryset=Presupuesto.objects.none(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ingreso
        fields = [
            "id",
            "categoria",
            "presupuesto",
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
            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=request.user,
                tipo="INGRESO",
                activa=True
            )

            self.fields["presupuesto"].queryset = Presupuesto.objects.filter(
                usuario=request.user
            )


class GastoSerializer(serializers.ModelSerializer):

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.none()
    )

    presupuesto = serializers.PrimaryKeyRelatedField(
        queryset=Presupuesto.objects.none(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Gasto
        fields = [
            "id",
            "categoria",
            "presupuesto",
            "monto",
            "fecha",
            "descripcion",
            "creado"
        ]
        read_only_fields = ["id", "creado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=request.user,
                tipo="GASTO",
                activa=True
            )

            self.fields["presupuesto"].queryset = Presupuesto.objects.filter(
                usuario=request.user
            )


class PresupuestoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Presupuesto
        fields = [
            "id",
            "nombre",
            "fecha_inicio",
            "fecha_fin",
            "monto_limite",
            "creado"
        ]
        read_only_fields = ["id", "creado"]


class ConfiguracionDistribucionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfiguracionDistribucion
        fields = [
            "porcentaje_necesidades",
            "porcentaje_gustos",
            "porcentaje_deudas",
            "porcentaje_ahorro",
            "porcentaje_inversion",
            "actualizada",
        ]
        read_only_fields = ["actualizada"]

    def validate(self, attrs):

        campos = [
            "porcentaje_necesidades",
            "porcentaje_gustos",
            "porcentaje_deudas",
            "porcentaje_ahorro",
            "porcentaje_inversion",
        ]

        valores_predeterminados = {
            "porcentaje_necesidades": Decimal("55"),
            "porcentaje_gustos": Decimal("5"),
            "porcentaje_deudas": Decimal("10"),
            "porcentaje_ahorro": Decimal("15"),
            "porcentaje_inversion": Decimal("15"),
        }

        porcentajes = {}

        for campo in campos:
            if campo in attrs:
                porcentajes[campo] = attrs[campo]
            elif self.instance:
                porcentajes[campo] = getattr(self.instance, campo)
            else:
                porcentajes[campo] = valores_predeterminados[campo]

        for campo, valor in porcentajes.items():
            if valor < 0 or valor > 100:
                raise serializers.ValidationError({
                    campo: "El porcentaje debe estar entre 0 y 100."
                })

        if sum(porcentajes.values()) != Decimal("100"):
            raise serializers.ValidationError(
                "Los porcentajes de distribución deben sumar exactamente 100 %."
            )

        return attrs


# ==========================================================
# VALIDACION DE CADA ASIGNACION DE LA DISTRIBUCION
# ==========================================================

class DetalleDistribucionEntradaSerializer(serializers.Serializer):

    DESTINOS = [
        "NECESIDADES",
        "GUSTOS",
        "DEUDAS",
        "AHORRO",
        "INVERSION",
    ]

    GRUPOS_CATEGORIA = {
        "NECESIDADES": "NECESIDADES",
        "GUSTOS": "GUSTOS",
        "DEUDAS": "DEUDAS",
    }

    destino = serializers.ChoiceField(choices=DESTINOS)

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.none(),
        required=False,
        allow_null=True
    )

    meta_ahorro = serializers.PrimaryKeyRelatedField(
        queryset=MetaAhorro.objects.none(),
        required=False,
        allow_null=True
    )

    monto = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01")
    )

    porcentaje = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        required=False,
        allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=request.user,
                tipo="GASTO",
                activa=True
            )

            self.fields["meta_ahorro"].queryset = MetaAhorro.objects.filter(
                usuario=request.user,
                estado="ACTIVA"
            )

    def validate(self, attrs):

        destino = attrs["destino"]
        categoria = attrs.get("categoria")
        meta = attrs.get("meta_ahorro")

        if destino in self.GRUPOS_CATEGORIA:

            if not categoria:
                raise serializers.ValidationError({
                    "categoria": "Este destino necesita una categoria."
                })

            if meta:
                raise serializers.ValidationError({
                    "meta_ahorro": "No se puede asociar una meta a este destino."
                })

            grupo_esperado = self.GRUPOS_CATEGORIA[destino]

            if categoria.grupo_distribucion != grupo_esperado:
                raise serializers.ValidationError({
                    "categoria": (
                        f"La categoria debe pertenecer al grupo {grupo_esperado}."
                    )
                })

        elif destino == "AHORRO":

            if categoria:
                raise serializers.ValidationError({
                    "categoria": "El destino ahorro no utiliza categorias de gasto."
                })

        elif destino == "INVERSION":

            if categoria or meta:
                raise serializers.ValidationError({
                    "destino": "La inversion se registra como dinero reservado."
                })

        return attrs


# ==========================================================
# VALIDACION COMPLETA ANTES DE CONFIRMAR LA DISTRIBUCION
# ==========================================================

class DistribucionConfirmacionSerializer(serializers.Serializer):

    ingreso = serializers.PrimaryKeyRelatedField(
        queryset=Ingreso.objects.none()
    )

    tipo = serializers.ChoiceField(
        choices=DistribucionIngreso.TIPOS
    )

    modalidad = serializers.ChoiceField(
        choices=DistribucionIngreso.MODALIDADES
    )

    detalles = DetalleDistribucionEntradaSerializer(
        many=True,
        allow_empty=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:

            self.fields["ingreso"].queryset = Ingreso.objects.filter(
                usuario=request.user
            )

            detalle = self.fields["detalles"].child

            detalle.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=request.user,
                tipo="GASTO",
                activa=True
            )

            detalle.fields["meta_ahorro"].queryset = MetaAhorro.objects.filter(
                usuario=request.user,
                estado="ACTIVA"
            )

    def validate(self, attrs):

        ingreso = attrs["ingreso"]
        tipo = attrs["tipo"]
        modalidad = attrs["modalidad"]
        detalles = attrs["detalles"]

        # Evitar distribuir dos veces el mismo ingreso.
        if DistribucionIngreso.objects.filter(ingreso=ingreso).exists():
            raise serializers.ValidationError({
                "ingreso": "Este ingreso ya tiene una distribucion registrada."
            })

        # Comprobar la modalidad.
        if tipo == "MANUAL" and modalidad != "NINGUNA":
            raise serializers.ValidationError({
                "modalidad": "La distribucion manual debe utilizar NINGUNA."
            })

        if tipo == "AUTOMATICA" and modalidad not in [
            "PREDETERMINADA",
            "PERSONALIZADA"
        ]:
            raise serializers.ValidationError({
                "modalidad": "Selecciona una modalidad automatica valida."
            })

        # Calcular el total distribuido.
        total_distribuido = sum(
            (detalle["monto"] for detalle in detalles),
            Decimal("0.00")
        )

        if total_distribuido > ingreso.monto:
            raise serializers.ValidationError({
                "detalles": "La distribucion supera el monto del ingreso."
            })

        # ==================================================
        # VALIDACIONES DE DISTRIBUCION MANUAL
        # ==================================================

        if tipo == "MANUAL":

            if any(
                detalle.get("porcentaje") is not None
                for detalle in detalles
            ):
                raise serializers.ValidationError({
                    "detalles": "La distribucion manual no utiliza porcentajes."
                })

        # ==================================================
        # VALIDACIONES DE DISTRIBUCION AUTOMATICA
        # ==================================================

        else:

            # Obtener los porcentajes correspondientes.
            if modalidad == "PREDETERMINADA":

                porcentajes = obtener_porcentajes_predeterminados()

            else:

                configuracion = ConfiguracionDistribucion.objects.filter(
                    usuario=ingreso.usuario
                ).first()

                if configuracion:
                    porcentajes = {
                        "NECESIDADES": configuracion.porcentaje_necesidades,
                        "GUSTOS": configuracion.porcentaje_gustos,
                        "DEUDAS": configuracion.porcentaje_deudas,
                        "AHORRO": configuracion.porcentaje_ahorro,
                        "INVERSION": configuracion.porcentaje_inversion,
                    }
                else:
                    porcentajes = obtener_porcentajes_predeterminados()

            # Calcular los importes oficiales esperados.
            try:
                resultado_esperado = calcular_distribucion_automatica(
                    ingreso.monto,
                    porcentajes
                )
            except ValueError as error:
                raise serializers.ValidationError({
                    "detalles": str(error)
                })

            importes_esperados = {
                detalle["destino"]: detalle["monto"]
                for detalle in resultado_esperado["detalles"]
            }

            # Comprobar cada destino por separado.
            for destino, importe_esperado in importes_esperados.items():

                importe_asignado = sum(
                    (
                        detalle["monto"]
                        for detalle in detalles
                        if detalle["destino"] == destino
                    ),
                    Decimal("0.00")
                )

                if importe_asignado != importe_esperado:
                    raise serializers.ValidationError({
                        "detalles": (
                            f"El destino {destino} debe recibir "
                            f"S/ {importe_esperado}, pero se intento "
                            f"asignar S/ {importe_asignado}."
                        )
                    })

            # La distribucion automatica debe cubrir todo el ingreso.
            if total_distribuido != ingreso.monto:
                raise serializers.ValidationError({
                    "detalles": (
                        "La distribucion automatica debe cubrir "
                        "todo el ingreso."
                    )
                })

            # Calcular el porcentaje real de cada detalle.
            # Se calcula sobre el ingreso completo, no sobre su destino.
            for detalle in detalles:

                porcentaje_real = (
                    detalle["monto"] / ingreso.monto * Decimal("100")
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )

                detalle["porcentaje"] = porcentaje_real

        # ==================================================
        # EVITAR CATEGORIAS REPETIDAS
        # ==================================================

        categorias = [
            detalle["categoria"].id
            for detalle in detalles
            if detalle.get("categoria")
        ]

        if len(categorias) != len(set(categorias)):
            raise serializers.ValidationError({
                "detalles": "No se puede repetir una categoria."
            })

        # ==================================================
        # EVITAR METAS REPETIDAS
        # ==================================================

        metas = [
            detalle["meta_ahorro"].id
            for detalle in detalles
            if detalle.get("meta_ahorro")
        ]

        if len(metas) != len(set(metas)):
            raise serializers.ValidationError({
                "detalles": "No se puede repetir una meta de ahorro."
            })

        # ==================================================
        # EVITAR RESERVAS GENERALES REPETIDAS
        # ==================================================

        reservas_generales = [
            detalle
            for detalle in detalles
            if detalle["destino"] == "AHORRO"
            and detalle.get("meta_ahorro") is None
        ]

        if len(reservas_generales) > 1:
            raise serializers.ValidationError({
                "detalles": "Solo puede existir una reserva general de ahorro."
            })

        # ==================================================
        # EVITAR ASIGNACIONES DE INVERSION REPETIDAS
        # ==================================================

        inversiones = [
            detalle
            for detalle in detalles
            if detalle["destino"] == "INVERSION"
        ]

        if len(inversiones) > 1:
            raise serializers.ValidationError({
                "detalles": "Solo puede existir una asignacion de inversion."
            })

        return attrs

