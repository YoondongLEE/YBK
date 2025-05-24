from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'info', views.FinanceInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('metal-prices/', views.get_metal_prices, name='metal-prices'),
    path('load-metal-prices/', views.load_metal_price_data, name='load-metal-prices'),
]