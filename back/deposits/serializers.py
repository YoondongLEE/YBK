from rest_framework import serializers
from .models import Bank, DepositProduct

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class DepositProductSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    
    class Meta:
        model = DepositProduct
        fields = '__all__'