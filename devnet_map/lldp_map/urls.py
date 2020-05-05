from django.contrib import admin
from django.urls import path

from . import views

app_name = 'lldp_map'
urlpatterns = [
    # обработка главной страницы
    path('', views.DevicesView.as_view(), name='devices_list'),
    # обработка страницы с топологией
    path('topology/', views.TopologyView.as_view(), name='topology'),
    # обработка страницы с разницей в топологии
    path('topology-diff/', views.TopologyDiffView.as_view(), name='topology_diff'),
]
