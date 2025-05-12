from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient, MedicalRecord, Appointment, Prescription, LabResult
from .serializers import (
    PatientSerializer, MedicalRecordSerializer, AppointmentSerializer,
    PrescriptionSerializer, LabResultSerializer
)

# Create your views here.

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'mrn']
    search_fields = ['user__first_name', 'user__last_name', 'mrn']
    ordering_fields = ['created_at', 'updated_at']

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient']
    search_fields = ['diagnosis', 'treatment', 'medications']
    ordering_fields = ['created_at', 'updated_at']

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status']
    search_fields = ['reason', 'notes']
    ordering_fields = ['date_time', 'created_at', 'updated_at']

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient']
    search_fields = ['medication', 'notes']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'updated_at']

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient']
    search_fields = ['test_name', 'result', 'notes']
    ordering_fields = ['date', 'created_at', 'updated_at']
