from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Railway Healthcheck를 위한 간단한 응답"""
    return JsonResponse({'status': 'healthy', 'message': 'Django server is running'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('deposits.urls')),
    path('api/accounts/', include('dj_rest_auth.urls')),
    path('api/accounts/signup/', include('dj_rest_auth.registration.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/finance-info/', include('finance_info.urls')),
    path('api/community/', include('community.urls')),
    path('api/finance-academy/', include('finance_academy.urls')),
]