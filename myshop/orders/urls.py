#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: urls.py
#
# Descripción:
#   En este archivo se definen las urls de la app de las órdenes.
#
#   Cada url debe tener la siguiente estructura:
#
#   path( url, vista, nombre_url )
#
#-------------------------------------------------------------------------

from django.urls import path
from . import views
from .models import OrderItem

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('cancel/', views.viewOrder, name='viewOrder'),
    path('delete/<int:id>/<int:order_id>', views.DeleteProductOrder, name='delete'),
    path('updateOrder/', views.sendMailCancel, name='updateOrder'),
]
