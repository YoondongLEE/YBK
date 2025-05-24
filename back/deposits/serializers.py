from rest_framework import serializers
from .models import Bank, DepositProduct, DepositOption, DepositSubscription, SavingProduct, SavingOption, SavingSubscription


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class DepositProductSerializer(serializers.ModelSerializer):
    bank_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DepositProduct
        fields = '__all__'
    
    def get_bank_name(self, obj):
        return obj.bank.kor_co_nm if obj.bank else None

class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = '__all__'

class SavingProductSerializer(serializers.ModelSerializer):
    bank_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SavingProduct
        fields = '__all__'
    
    def get_bank_name(self, obj):
        return obj.bank.kor_co_nm if obj.bank else None

class SavingSubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SavingSubscription
        fields = ['id', 'product', 'created_at', 'product_name', 'bank_name']
    
    def get_product_name(self, obj):
        return obj.product.fin_prdt_nm
    
    def get_bank_name(self, obj):
        return obj.product.bank.kor_co_nm