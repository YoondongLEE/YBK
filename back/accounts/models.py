from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    # groups와 user_permissions를 재정의하여 related_name 충돌 방지
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )
    
    # 가입한 예금 상품 목록 (다대다 관계) - related_name 수정
    subscribed_deposits = models.ManyToManyField(
        'deposits.DepositProduct',
        related_name='user_subscribers',  # 변경
        blank=True,
        verbose_name="가입한 정기예금 상품"
    )
    
    # 가입한 적금 상품 추가
    subscribed_savings = models.ManyToManyField(
        'deposits.SavingProduct',
        related_name='user_subscribers',  # 변경
        blank=True,
        verbose_name="가입한 정기적금 상품"
    )

    # 새로운 필드 추가
    # 저장된 YouTube 영상 정보를 JSON 형태로 저장
    saved_videos = models.JSONField(default=list, blank=True)
    
    # 저장된 YouTube 채널 정보를 JSON 형태로 저장
    saved_channels = models.JSONField(default=list, blank=True)