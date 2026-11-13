
from django.contrib import admin
from .models import (
    Categoria,
    Presupuesto,
    Ingreso,
    DistribucionIngreso,
    DetalleDistribucion,
    Gasto,
    ConfiguracionFinanciera,
)


admin.site.register(Categoria)
admin.site.register(Presupuesto)
admin.site.register(Ingreso)
admin.site.register(DistribucionIngreso)
admin.site.register(DetalleDistribucion)
admin.site.register(Gasto)
admin.site.register(ConfiguracionFinanciera)
