from django.contrib import admin
from .models import Patient, MedicalRecord, Appointment, Prescription, LabResult

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'mrn', 'date_of_birth', 'gender', 'phone_number')
    search_fields = ('user__username', 'user__email', 'mrn')
    list_filter = ('gender', 'created_at')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'updated_at')
    search_fields = ('patient__user__username', 'diagnosis', 'treatment')
    list_filter = ('created_at', 'updated_at')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date_time', 'status', 'reason')
    search_fields = ('patient__user__username', 'reason', 'notes')
    list_filter = ('status', 'date_time', 'created_at')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medication', 'dosage', 'start_date', 'end_date')
    search_fields = ('patient__user__username', 'medication', 'notes')
    list_filter = ('start_date', 'end_date', 'created_at')

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test_name', 'date', 'result')
    search_fields = ('patient__user__username', 'test_name', 'result')
    list_filter = ('date', 'created_at')
