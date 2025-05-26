from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'age', 
            'assets', 
            'annual_income',
            'savings_tendency',
            'investment_tendency',
            'preferred_bank'
        ]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'age', 
            'assets', 
            'annual_income',
            'savings_tendency',
            'investment_tendency', 
            'preferred_bank'
        ]
        
    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("나이는 0세 이상 150세 이하로 입력해주세요.")
        return value
    
    def validate_assets(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("자산은 0원 이상 입력해주세요.")
        return value
    
    def validate_annual_income(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("연봉은 0원 이상 입력해주세요.")
        return value


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user