"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from kernel import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('accounts/login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    # path('forgot/', views.forgot, name='forgot'),
    path('change/', views.change_password, name='change'),

    # para administradores y responsables
    path('buscar/', views.buscar, name='buscar'),

    # para administradores
    path('admin/', admin.site.urls),
    path('servicentros/', views.servicentros, name='servicentros'),
    path('add_servicentro/', views.add_servicentro, name='add_servicentro'),
    path('responsables/', views.responsables, name='responsables'),
    path('add_responsable/', views.add_responsable, name='add_responsable'),

    # para responsables
    path('add_combustible/', views.add_combustible, name='add_combustible'),
    path('procesar_gasolina/', views.procesar_gasolina, name='procesar_gasolina'),
    path('procesar_diesel/', views.procesar_diesel, name='procesar_diesel'),
    path('dar_baja_cola/', views.dar_baja_cola, name='dar_baja_cola'),

    # para clientes
    path('profile/', views.profile, name='profile'),
    path('autos/', views.autos, name='autos'),
    path('add_auto/', views.add_auto, name='add_auto'),
    path('reservas/', views.reservas, name='reservas'),
    path('add_reserva/', views.add_reserva, name='add_reserva'),
    path('del_reserva/<str:pk_turno>', views.del_reserva, name='del_reserva'),
    path('del_profile/<str:pk_chofer>', views.del_profile, name='del_profile'),

    # para todos
    path('tiempo_real_gasolina/<str:pk_servi>', views.tiempo_real_gasolina, name='tiempo_real_gasolina'),
    path('tiempo_real_diesel/<str:pk_servi>', views.tiempo_real_diesel, name='tiempo_real_diesel'),

]
