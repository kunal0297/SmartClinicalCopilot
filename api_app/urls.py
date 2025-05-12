from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    PatientViewSet,
    MedicalRecordViewSet,
    AppointmentViewSet,
    PrescriptionViewSet,
    LabResultViewSet
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'lab-results', LabResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 