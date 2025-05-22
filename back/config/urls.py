from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('dj_rest_auth.urls')),
    path('api/accounts/signup/', include('dj_rest_auth.registration.urls')),
    path('api/finance-academy/', include('finance_academy.urls')),
    path('api/finance-info/', include('finance_info.urls')),
]