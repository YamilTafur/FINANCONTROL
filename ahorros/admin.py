
from django.contrib import admin
from .models import (
    MetaAhorro,
    AporteAhorro,
    ConfiguracionProteccion,
)


admin.site.register(MetaAhorro)
admin.site.register(AporteAhorro)
admin.site.register(ConfiguracionProteccion)
