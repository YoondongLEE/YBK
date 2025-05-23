from django.db import models
from django.conf import settings

class Bank(models.Model):
    fin_co_no = models.CharField(max_length=20, unique=True)
    kor_co_nm = models.CharField(max_length=100)

    def __str__(self):
        return self.kor_co_nm

class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=50, unique=True)
    fin_prdt_nm = models.CharField(max_length=200)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='products')
    join_way = models.CharField(max_length=200, null=True, blank=True)
    mtrt_int = models.CharField(max_length=50, null=True, blank=True)
    dcls_month = models.CharField(max_length=6, null=True, blank=True)
    etc          = models.JSONField(null=True, blank=True)   # ← 이 줄 추가


    def __str__(self):
        return f"{self.bank.kor_co_nm} - {self.fin_prdt_nm}"

