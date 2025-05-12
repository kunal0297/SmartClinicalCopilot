from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'medical-records', views.MedicalRecordViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'prescriptions', views.PrescriptionViewSet)
router.register(r'lab-results', views.LabResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 