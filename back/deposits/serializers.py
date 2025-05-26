from rest_framework import serializers
from .models import Bank, DepositProduct, DepositOption, DepositSubscription, SavingProduct, SavingOption, SavingSubscription


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class DepositProductSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = DepositProduct
        fields = '__all__'
    
    def get_options(self, obj):
        # options 필드가 JSONField로 저장되어 있다면 그대로 반환
        if hasattr(obj, 'options') and obj.options:
            return obj.options
        # 없다면 deposit_options 관계에서 가져오기
        return list(obj.deposit_options.all().values())

class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = '__all__'

class SavingProductSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = SavingProduct
        fields = '__all__'
    
    def get_options(self, obj):
        # options 필드가 JSONField로 저장되어 있다면 그대로 반환
        if hasattr(obj, 'options') and obj.options:
            return obj.options
        # 없다면 saving_options 관계에서 가져오기
        return list(obj.saving_options.all().values())

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