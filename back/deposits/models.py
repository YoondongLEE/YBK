from django.db import models
from django.conf import settings
from django.db.models import JSONField

class Bank(models.Model):
    """은행/금융기관 정보"""
    fin_co_no = models.TextField(primary_key=True)  # 금융회사 코드
    kor_co_nm = models.TextField()  # 금융회사명
    sector_code = models.TextField(null=True, blank=True)  # 권역코드
    sector_name = models.TextField(null=True, blank=True)  # 권역명
    
    def __str__(self):
        return self.kor_co_nm

class DepositProduct(models.Model):
    """정기예금 상품 정보"""
    fin_prdt_cd = models.TextField(primary_key=True)  # 금융상품 코드
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='deposits')  # 은행 참조
    fin_prdt_nm = models.TextField()  # 금융 상품명
    join_way = models.TextField(null=True, blank=True)  # 가입 방법
    mtrt_int = models.TextField(null=True, blank=True)  # 만기 후 이자율
    spcl_cnd = models.TextField(null=True, blank=True)  # 우대조건
    join_member = models.TextField(null=True, blank=True)  # 가입대상
    join_deny = models.TextField(null=True, blank=True)  # 가입제한
    etc_note = models.TextField(null=True, blank=True)  # 기타 유의사항
    max_limit = models.IntegerField(null=True, blank=True)  # 최고한도
    dcls_strt_day = models.TextField()  # 공시 시작일
    dcls_end_day = models.TextField(null=True, blank=True)  # 공시 종료일
    fin_co_subm_day = models.TextField()  # 금융회사 제출일
    sector_code = models.TextField(null=True, blank=True)  # 권역코드
    options = JSONField(default=list)  # 금리 옵션 정보 (JSON 형태로 저장)
    
    # subscribers 필드 제거 - User 모델에서만 관계 정의
    
    def __str__(self):
        return f"{self.fin_prdt_nm} - {self.bank.kor_co_nm}"

class DepositOption(models.Model):
    """정기예금 금리 옵션 정보"""
    product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='deposit_options')
    intr_rate_type = models.TextField()  # 금리유형
    intr_rate_type_nm = models.TextField()  # 금리유형명
    save_trm = models.TextField()  # 저축기간
    intr_rate = models.TextField(null=True, blank=True)  # 기본금리
    intr_rate2 = models.TextField(null=True, blank=True)  # 우대금리
    
    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"

class DepositSubscription(models.Model):
    """사용자의 예금 상품 가입 정보"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"

class SavingProduct(models.Model):
    """정기적금 상품 정보"""
    fin_prdt_cd = models.TextField(primary_key=True)  # 금융상품 코드
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='savings')  # 은행 참조
    fin_prdt_nm = models.TextField()  # 금융 상품명
    join_way = models.TextField(null=True, blank=True)  # 가입 방법
    mtrt_int = models.TextField(null=True, blank=True)  # 만기 후 이자율
    spcl_cnd = models.TextField(null=True, blank=True)  # 우대조건
    join_member = models.TextField(null=True, blank=True)  # 가입대상
    join_deny = models.TextField(null=True, blank=True)  # 가입제한
    etc_note = models.TextField(null=True, blank=True)  # 기타 유의사항
    max_limit = models.IntegerField(null=True, blank=True)  # 최고한도
    dcls_strt_day = models.TextField()  # 공시 시작일
    dcls_end_day = models.TextField(null=True, blank=True)  # 공시 종료일
    fin_co_subm_day = models.TextField()  # 금융회사 제출일
    sector_code = models.TextField(null=True, blank=True)  # 권역코드
    options = JSONField(default=list)  # 금리 옵션 정보 (JSON 형태로 저장)
    
    # subscribers 필드 제거 - User 모델에서만 관계 정의
    
    def __str__(self):
        return f"{self.fin_prdt_nm} - {self.bank.kor_co_nm}"

class SavingOption(models.Model):
    """정기적금 금리 옵션 정보"""
    product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE, related_name='saving_options')
    intr_rate_type = models.TextField()  # 금리유형
    intr_rate_type_nm = models.TextField()  # 금리유형명
    save_trm = models.TextField()  # 저축기간
    intr_rate = models.TextField(null=True, blank=True)  # 기본금리
    intr_rate2 = models.TextField(null=True, blank=True)  # 우대금리
    
    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"

class SavingSubscription(models.Model):
    """사용자의 적금 상품 가입 정보"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"