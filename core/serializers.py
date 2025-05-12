from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, MedicalRecord, Appointment, Prescription, LabResult

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')
    
    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create patient with user
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PrescriptionSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class LabResultSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    
    class Meta:
        model = LabResult
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 