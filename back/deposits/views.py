from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from .models import Bank, DepositProduct
from .serializers import BankSerializer, DepositProductSerializer

API_KEY = 'b70cc94eccb131aefe4ee81723903f12'
BASE_URL = 'http://finlife.fss.or.kr/finlifeapi'

@api_view(['GET'])
def save_deposit_products(request):
    url = f'{BASE_URL}/depositProductsSearch.json'
    params = {
        'auth': API_KEY,
        'topFinGrpNo': '020000',  # 예적금
        'pageNo': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    banks_data    = data.get('result', {}).get('baseList', [])
    products_data = data.get('result', {}).get('baseList', [])  # baseList에 상품 정보가 담겨 있습니다

    # 은행 정보 저장
    for bank_data in banks_data:
        Bank.objects.get_or_create(
            fin_co_no=bank_data.get('fin_co_no'),
            defaults={'kor_co_nm': bank_data.get('kor_co_nm')}
        )

    # 상품 정보 저장
    for product_data in products_data:
        bank = Bank.objects.get(fin_co_no=product_data.get('fin_co_no'))
        DepositProduct.objects.get_or_create(
            fin_prdt_cd=product_data.get('fin_prdt_cd'),
            defaults={
                'bank': bank,
                'fin_prdt_nm': product_data.get('fin_prdt_nm'),
                'join_way': product_data.get('join_way'),
                'mtrt_int': product_data.get('mtrt_int'),
                'dcls_month': product_data.get('dcls_month'),
            }
        )

    # optionList 에 기간별 금리 정보가 들어 있습니다!
    options = data.get('result', {}).get('optionList', [])

    for opt in options:
        from collections import defaultdict
    
        # 옵션들을 상품별로 묶어서
        opts_by_product = defaultdict(list)
        for opt in options:
            opts_by_product[opt['fin_prdt_cd']].append(opt)
    
        # 각 상품마다 등급별 금리 리스트 전체 저장
        for prdt_cd, opt_list in opts_by_product.items():
            try:
                dp = DepositProduct.objects.get(fin_prdt_cd=prdt_cd)
            except DepositProduct.DoesNotExist:
                continue
            dp.etc = opt_list            # <-- 리스트 전체 할당
            # 최대금리 계산(예시)
            dp.max_rate = max(float(o.get('intr_rate', 0)) for o in opt_list)
            dp.save()

    return Response({'message': '데이터가 성공적으로 저장되었습니다.'})

class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class DepositProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
