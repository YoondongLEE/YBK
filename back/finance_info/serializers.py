from rest_framework import serializers
from .models import FinanceInfo

class FinanceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceInfo
        fields = '__all__'