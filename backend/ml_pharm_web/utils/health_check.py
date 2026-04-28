from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    try:
        connection.ensure_connection()
        return JsonResponse({
            "status": "healthy",
            "version": settings.GIT_COMMIT_HASH
        }, status=200)
    
    except Exception:
        return JsonResponse({
            "status": "unhealthy",
            "version": settings.GIT_COMMIT_HASH
        }, status=503)
