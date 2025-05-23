from django.db import models

class Bank(models.Model):
    fin_co_no = models.CharField(max_length=20, unique=True)
    kor_co_nm = models.CharField(max_length=100)
    sector_code = models.CharField(max_length=20, blank=True, null=True)  # 권역코드
    sector_name = models.CharField(max_length=50, blank=True, null=True)  # 권역명
    
    def __str__(self):
        return self.kor_co_nm

class DepositProduct(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='deposit_products')
    fin_prdt_cd = models.CharField(max_length=100, unique=True)  # 금융상품코드
    fin_prdt_nm = models.CharField(max_length=200)  # 금융상품명
    join_way = models.CharField(max_length=200)  # 가입방법
    mtrt_int = models.TextField()  # 만기 후 이자율
    spcl_cnd = models.TextField(blank=True, null=True)  # 우대조건
    dcls_month = models.CharField(max_length=10)  # 공시 제출월
    etc = models.JSONField(blank=True, null=True)  # 기타 금리 정보
    max_rate = models.FloatField(default=0)  # 최대 금리
    sector_code = models.CharField(max_length=20, blank=True, null=True)  # 권역코드
    
    def __str__(self):
        return f"{self.bank.kor_co_nm} - {self.fin_prdt_nm}"