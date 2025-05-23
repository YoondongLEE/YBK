from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('dj_rest_auth.urls')),
    path('api/accounts/signup/', include('dj_rest_auth.registration.urls')),
    path('api/accounts/', include('accounts.urls')),  # 계정 API
    path('api/', include('deposits.urls')),
]