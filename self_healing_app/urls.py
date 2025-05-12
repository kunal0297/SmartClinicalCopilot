from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.health_status, name='health_status'),
    path('metrics/', views.system_metrics, name='system_metrics'),
    path('alerts/', views.alerts, name='alerts'),
] 