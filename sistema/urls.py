from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login',views.login_view,name="login"),
    path('logout',views.logout_view,name="logout"),
    path('inicio',views.inicio,name="inicio"),
    path('turnos',views.turnos,name="turnos"),
    path('pacientes',views.pacientes,name='pacientes'),
    path('articulos',views.articulos,name='articulos'),
    path('pedidos',views.pedidos,name='pedidos'),
    path('pedidos_agregar',views.pedidosAgregar,name='pedidosAgregar'),
    path('reportes',views.reportes,name='reportes'),
 
]
 
