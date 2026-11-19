
from django.urls import path
from . import views

urlpatterns = [
    path("", views.panel_financiero, name="panel_financiero"),

    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/nueva/", views.crear_categoria, name="crear_categoria"),

    path("ingresos/", views.lista_ingresos, name="lista_ingresos"),
    path("ingresos/nuevo/", views.crear_ingreso, name="crear_ingreso"),

    path("gastos/", views.lista_gastos, name="lista_gastos"),
    path("gastos/nuevo/", views.crear_gasto, name="crear_gasto"),
]
