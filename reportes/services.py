
from decimal import Decimal

from django.db.models import Sum

from finanzas.models import (
    Categoria,
    Ingreso,
    Gasto,
    DetalleDistribucion,
)


def obtener_resumen_financiero(usuario, fecha_inicio=None, fecha_fin=None):
    """
    Calcula el resumen financiero de un usuario.
    Permite filtrar los resultados por fechas.
    """

    ingresos = Ingreso.objects.filter(usuario=usuario)
    gastos = Gasto.objects.filter(usuario=usuario)

    if fecha_inicio:
        ingresos = ingresos.filter(fecha__gte=fecha_inicio)
        gastos = gastos.filter(fecha__gte=fecha_inicio)

    if fecha_fin:
        ingresos = ingresos.filter(fecha__lte=fecha_fin)
        gastos = gastos.filter(fecha__lte=fecha_fin)

    total_ingresos = ingresos.aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0.00')

    total_gastos = gastos.aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0.00')

    balance = total_ingresos - total_gastos

    return {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance': balance,
    }


def obtener_saldos_por_categoria(usuario, fecha_inicio=None, fecha_fin=None):
    """
    Calcula el saldo disponible de cada categoría de gasto.
    """

    categorias = Categoria.objects.filter(
        usuario=usuario,
        tipo='GASTO',
        activa=True
    )

    resultados = []

    for categoria in categorias:

        distribuciones = DetalleDistribucion.objects.filter(
            categoria=categoria,
            distribucion__ingreso__usuario=usuario
        )

        gastos = Gasto.objects.filter(
            usuario=usuario,
            categoria=categoria
        )

        if fecha_inicio:
            distribuciones = distribuciones.filter(
                distribucion__ingreso__fecha__gte=fecha_inicio
            )
            gastos = gastos.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            distribuciones = distribuciones.filter(
                distribucion__ingreso__fecha__lte=fecha_fin
            )
            gastos = gastos.filter(fecha__lte=fecha_fin)

        total_asignado = distribuciones.aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')

        total_gastado = gastos.aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')

        resultados.append({
            'categoria': categoria.nombre,
            'total_asignado': total_asignado,
            'total_gastado': total_gastado,
            'saldo_disponible': total_asignado - total_gastado,
        })

    return resultados
