from django.urls import path
from analytics import views

urlpatterns = [
    path('health/', views.health),
    path('machines/', views.machines),
    path('kpis/', views.kpis),
    path('machine-load/', views.machine_load),
    path('load-profiles/', views.load_profiles),
    path('energy-consumption/', views.energy_consumption),
    path('reliability/summary/', views.reliability_summary),
    path('alerts/', views.alerts),
    path('data-quality/', views.data_quality),
    path('engineering-summary/', views.engineering_summary),
]
