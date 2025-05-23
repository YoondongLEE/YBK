from django.urls import path, include
from rest_framework import routers
from .views import BankViewSet, DepositProductViewSet, save_deposit_products

router = routers.DefaultRouter()
router.register(r'banks', BankViewSet)
router.register(r'deposits', DepositProductViewSet)

urlpatterns = [
    path('load-deposits/', save_deposit_products, name='load-deposits'),
    path('', include(router.urls)),
]