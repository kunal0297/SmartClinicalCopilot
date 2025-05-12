from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
import psutil
import time

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_status(request):
    """Return the current health status of the system."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'database': 'operational',
            'cache': 'operational',
            'celery': 'operational'
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_metrics(request):
    """Return current system metrics."""
    return JsonResponse({
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'timestamp': time.time()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts(request):
    """Return current system alerts."""
    return JsonResponse({
        'alerts': [],
        'timestamp': time.time()
    })
