from django.contrib.auth.models import AbstractUser
from django.db import models

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
    
    # 정기예금 상품과의 관계 - through 옵션으로 중간 테이블 지정
    subscribed_deposits = models.ManyToManyField(
        'deposits.DepositProduct',
        through='deposits.DepositSubscription',
        related_name='subscribers',
        blank=True,
        verbose_name="가입한 정기예금 상품"
    )
    
    # 정기적금 상품과의 관계 - through 옵션으로 중간 테이블 지정
    subscribed_savings = models.ManyToManyField(
        'deposits.SavingProduct',
        through='deposits.SavingSubscription',
        related_name='subscribers',
        blank=True,
        verbose_name="가입한 정기적금 상품"
    )
    
    # 저장된 YouTube 영상 정보를 JSON 형태로 저장
    saved_videos = models.JSONField(default=list, blank=True)
    
    # 저장된 YouTube 채널 정보를 JSON 형태로 저장
    saved_channels = models.JSONField(default=list, blank=True)
    
    # 개인정보 필드들
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="나이")
    assets = models.BigIntegerField(null=True, blank=True, verbose_name="자산 (원)")
    annual_income = models.BigIntegerField(null=True, blank=True, verbose_name="연봉 (원)")

    # 포트폴리오 필드들
    SAVINGS_TENDENCY_CHOICES = [
        ('conservative', '안정형'),
        ('moderate', '균형형'),
        ('aggressive', '적극형'),
    ]
    
    INVESTMENT_TENDENCY_CHOICES = [
        ('very_conservative', '매우 보수적'),
        ('conservative', '보수적'),
        ('moderate', '중립적'),
        ('aggressive', '적극적'),
        ('very_aggressive', '매우 적극적'),
    ]
    
    savings_tendency = models.CharField(
        max_length=20,
        choices=SAVINGS_TENDENCY_CHOICES,
        blank=True,
        null=True,
        verbose_name="저축성향"
    )
    
    investment_tendency = models.CharField(
        max_length=20,
        choices=INVESTMENT_TENDENCY_CHOICES,
        blank=True,
        null=True,
        verbose_name="투자성향"
    )
    
    preferred_bank = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="선호 은행 코드"
    )

    def __str__(self):
        return self.username