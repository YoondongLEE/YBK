from rest_framework import serializers
from .models import FinanceInfo, MetalPrice

class FinanceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceInfo
        fields = '__all__'

class MetalPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetalPrice
        fields = ['id', 'metal_type', 'date', 'price']