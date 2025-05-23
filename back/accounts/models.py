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
    
    # 가입한 예금 상품 목록 (다대다 관계) - 문자열 참조로 수정
    subscribed_deposits = models.ManyToManyField(
        'deposits.DepositProduct',  # 문자열 참조로 변경
        related_name='subscribers',
        blank=True,
        verbose_name="가입한 정기예금 상품"
    )