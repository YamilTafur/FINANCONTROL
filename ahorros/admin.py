
from django.contrib import admin
from .models import (
    MetaAhorro,
    AporteAhorro,
    ConfiguracionProteccion,
    RetiroAhorro,
)


admin.site.register(MetaAhorro)
admin.site.register(AporteAhorro)
admin.site.register(ConfiguracionProteccion)
admin.site.register(RetiroAhorro)
