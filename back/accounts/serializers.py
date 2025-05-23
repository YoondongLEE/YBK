from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'subscribed_deposits')
        read_only_fields = ('username',)

class UserDetailSerializer(serializers.ModelSerializer):
    # deposits.serializers에서 임포트하는 대신 여기서 필요한 필드만 정의
    subscribed_deposits = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'subscribed_deposits')
        read_only_fields = ('username',)
    
    def get_subscribed_deposits(self, user):
        from deposits.serializers import DepositProductSerializer
        return DepositProductSerializer(user.subscribed_deposits.all(), many=True).data