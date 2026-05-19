from django.urls import path
from analytics import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from analytics.views import machine_detail

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
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("machines/<str:machine_code>/", machine_detail, name="machine-detail"),
]
