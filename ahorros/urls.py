
from rest_framework.routers import DefaultRouter

from .views import (
    MetaAhorroViewSet,
    AporteAhorroViewSet,
    ConfiguracionProteccionViewSet,
)


router = DefaultRouter()

router.register(
    "metas",
    MetaAhorroViewSet,
    basename="api-metas-ahorro"
)

router.register(
    "aportes",
    AporteAhorroViewSet,
    basename="api-aportes-ahorro"
)

router.register(
    "protecciones",
    ConfiguracionProteccionViewSet,
    basename="api-protecciones-ahorro"
)

urlpatterns = router.urls
