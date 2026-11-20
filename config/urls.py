
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from finanzas.views import (
    CategoriaViewSet,
    IngresoViewSet,
    GastoViewSet,
    PresupuestoViewSet,
    resumen_api,
    resumen_presupuestos_api,
    configuracion_distribucion_api,
    previsualizar_distribucion_api,
    confirmar_distribucion_api,
)

from usuarios.api_views import (
    obtener_csrf,
    iniciar_sesion_api,
    cerrar_sesion_api,
)
from ahorros.views import (
    MetaAhorroViewSet,
    AporteAhorroViewSet,
    ConfiguracionProteccionViewSet,
    RetiroAhorroViewSet,
    resumen_ahorros_api,
)
# Router de la API
router = DefaultRouter()

router.register(
    "categorias",
    CategoriaViewSet,
    basename="api-categorias"
)

router.register(
    "ingresos",
    IngresoViewSet,
    basename="api-ingresos"
)

router.register(
    "gastos",
    GastoViewSet,
    basename="api-gastos"
)

router.register(
    "presupuestos",
    PresupuestoViewSet,
    basename="api-presupuestos"
)

router.register(
    "ahorros/metas",
    MetaAhorroViewSet,
    basename="api-metas-ahorro"
)

router.register(
    "ahorros/aportes",
    AporteAhorroViewSet,
    basename="api-aportes-ahorro"
)

router.register(
    "ahorros/protecciones",
    ConfiguracionProteccionViewSet,
    basename="api-protecciones-ahorro"
)

router.register(
    "ahorros/retiros",
    RetiroAhorroViewSet,
    basename="api-retiros-ahorro"
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Autenticación
    path("api/csrf/", obtener_csrf, name="api_csrf"),
    path("api/login/", iniciar_sesion_api, name="api_login"),
    path("api/logout/", cerrar_sesion_api, name="api_logout"),

    # Resúmenes
    path("api/resumen/", resumen_api, name="api_resumen"),
    path(
        "api/presupuestos/resumen/",
        resumen_presupuestos_api,
        name="resumen_presupuestos"
    ),

    path(
    "api/distribucion/configuracion/",
    configuracion_distribucion_api,
    name="api_configuracion_distribucion"
    ),
        path(
        "api/distribucion/previsualizar/",
        previsualizar_distribucion_api,
        name="api_previsualizar_distribucion"
    ),

    path(
        "api/distribucion/confirmar/",
        confirmar_distribucion_api,
        name="api_confirmar_distribucion"
    ),

    path(
        "api/ahorros/resumen/",
        resumen_ahorros_api,
        name="api_resumen_ahorros"
),

    # API REST
    path("api/", include(router.urls)),

    # Páginas tradicionales
    path("finanzas/", include("finanzas.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("usuarios.urls")),
]
