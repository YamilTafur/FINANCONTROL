
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


# Destinos disponibles en FINANCONTROL
DESTINOS = [
    "NECESIDADES",
    "GUSTOS",
    "DEUDAS",
    "AHORRO",
    "INVERSION",
]

# Distribución predeterminada aprobada para el proyecto
PORCENTAJES_PREDETERMINADOS = {
    "NECESIDADES": Decimal("55.00"),
    "GUSTOS": Decimal("5.00"),
    "DEUDAS": Decimal("10.00"),
    "AHORRO": Decimal("15.00"),
    "INVERSION": Decimal("15.00"),
}

CENTAVO = Decimal("0.01")
CERO = Decimal("0.00")


def convertir_decimal(valor):
    """Convierte un valor a Decimal y evita errores de precisión."""
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El valor ingresado no es un número válido.")

    if not numero.is_finite():
        raise ValueError("El valor debe ser un número finito.")

    return numero


def validar_porcentajes(porcentajes):
    """Comprueba que los cinco porcentajes sean válidos y sumen 100 %."""
    if not isinstance(porcentajes, dict):
        raise ValueError("Los porcentajes deben enviarse como un objeto.")

    if set(porcentajes.keys()) != set(DESTINOS):
        raise ValueError("Debe indicar los cinco destinos de distribución.")

    resultado = {}

    for destino in DESTINOS:
        porcentaje = convertir_decimal(porcentajes[destino])

        if porcentaje < 0 or porcentaje > 100:
            raise ValueError(
                f"El porcentaje de {destino} debe estar entre 0 y 100."
            )

        resultado[destino] = porcentaje

    if sum(resultado.values()) != Decimal("100"):
        raise ValueError("La suma de los porcentajes debe ser exactamente 100 %.")

    return resultado


def obtener_porcentajes_predeterminados():
    """Devuelve una copia de los porcentajes predeterminados."""
    return PORCENTAJES_PREDETERMINADOS.copy()


def calcular_distribucion_automatica(monto, porcentajes):
    """
    Calcula la distribución automática.

    El último destino recibe el ajuste de redondeo para garantizar
    que la suma distribuida sea exactamente igual al ingreso.
    """
    monto = convertir_decimal(monto)

    if monto <= 0:
        raise ValueError("El ingreso debe ser mayor que cero.")

    monto = monto.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    porcentajes = validar_porcentajes(porcentajes)

    detalles = []
    total_distribuido = CERO

    for indice, destino in enumerate(DESTINOS):
        porcentaje = porcentajes[destino]

        if indice == len(DESTINOS) - 1:
            cantidad = monto - total_distribuido
        else:
            cantidad = (
                monto * porcentaje / Decimal("100")
            ).quantize(CENTAVO, rounding=ROUND_HALF_UP)

        detalles.append({
            "destino": destino,
            "monto": cantidad,
            "porcentaje": porcentaje,
        })

        total_distribuido += cantidad

    return {
        "detalles": detalles,
        "total_ingreso": monto,
        "total_distribuido": total_distribuido,
        "pendiente": monto - total_distribuido,
    }


def calcular_distribucion_manual(monto, asignaciones):
    """
    Calcula una distribución manual.

    Permite dejar una parte del ingreso sin asignar,
    pero nunca distribuir más dinero del disponible.
    """
    monto = convertir_decimal(monto)

    if monto <= 0:
        raise ValueError("El ingreso debe ser mayor que cero.")

    monto = monto.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    if not isinstance(asignaciones, dict) or not asignaciones:
        raise ValueError("Debe ingresar al menos una asignación.")

    detalles = []
    total_distribuido = CERO
    destinos_utilizados = set()

    for destino, valor in asignaciones.items():
        if destino not in DESTINOS:
            raise ValueError(f"El destino {destino} no es válido.")

        if destino in destinos_utilizados:
            raise ValueError(f"El destino {destino} está repetido.")

        cantidad = convertir_decimal(valor)

        if cantidad < 0:
            raise ValueError("Las cantidades no pueden ser negativas.")

        cantidad = cantidad.quantize(CENTAVO, rounding=ROUND_HALF_UP)

        if cantidad == 0:
            continue

        total_distribuido += cantidad

        detalles.append({
            "destino": destino,
            "monto": cantidad,
            "porcentaje": None,
        })

        destinos_utilizados.add(destino)

    if total_distribuido > monto:
        raise ValueError(
            "La cantidad distribuida supera el ingreso disponible."
        )

    return {
        "detalles": detalles,
        "total_ingreso": monto,
        "total_distribuido": total_distribuido,
        "pendiente": monto - total_distribuido,
    }
