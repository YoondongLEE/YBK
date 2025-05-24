from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'banks', views.BankViewSet)
router.register(r'deposits', views.DepositProductViewSet)
router.register(r'savings', views.SavingProductViewSet)

urlpatterns = [
    # URL 패턴 이름 변경: 'subscriptions' -> 'user-subscriptions'
    path('deposits/user-subscriptions/', views.get_user_subscribed_deposits, name='user-subscribed-deposits'),
    path('savings/user-subscriptions/', views.get_user_subscribed_savings, name='user-subscribed-savings'),
    
    path('', include(router.urls)),
    path('save-deposit-products/', views.save_deposit_products, name='save-deposit-products'),
    path('save-saving-products/', views.save_saving_products, name='save-saving-products'),
    path('sectors/', views.get_sectors, name='get-sectors'),
    path('deposits/<str:pk>/subscribe/', views.subscribe_deposit, name='subscribe-deposit'),
    path('deposits/<str:pk>/check-subscription/', views.check_subscription, name='check-deposit-subscription'),
    path('savings/<str:pk>/subscribe/', views.subscribe_saving, name='subscribe-saving'),
    path('savings/<str:pk>/check-subscription/', views.check_saving_subscription, name='check-saving-subscription'),
]