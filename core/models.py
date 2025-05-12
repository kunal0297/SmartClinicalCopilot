from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mrn = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.mrn}"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment = models.TextField()
    medications = models.TextField()
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.patient} - {self.created_at}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment for {self.patient} on {self.date_time}"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medication} for {self.patient}"

class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    result = models.TextField()
    reference_range = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient} on {self.date}"
