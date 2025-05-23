from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'banks', views.BankViewSet)
router.register(r'deposits', views.DepositProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('save-deposit-products/', views.save_deposit_products, name='save_deposit_products'),
    path('sectors/', views.get_sectors, name='get_sectors'),
    path('deposits/<int:pk>/subscribe/', views.subscribe_deposit, name='subscribe_deposit'),
    path('deposits/<int:pk>/check-subscription/', views.check_subscription, name='check_subscription'),
]