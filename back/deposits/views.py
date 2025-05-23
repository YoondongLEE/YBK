import os
import json
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
import requests
import traceback
from .models import Bank, DepositProduct
from .serializers import BankSerializer, DepositProductSerializer

# .env 파일에서 API 키 가져오기
API_KEY = os.environ.get('FINLIFE_API_KEY', 'eb9f3d19062bbbc32015258aabea7ed3')

# 권역코드 정의
SECTOR_CODES = {
    '020000': '은행',
    '030200': '여신전문',
    '030300': '저축은행',
    '050000': '보험',
    '060000': '금융투자'
}

@api_view(['GET'])
@permission_classes([AllowAny])  # 명시적으로 모든 사용자 접근 허용
def save_deposit_products(request):
    """금융감독원 API에서 정기예금 상품 정보를 가져와 DB에 저장"""
    
    # 권역코드 파라미터 가져오기 (기본값: 모든 권역)
    selected_sector = request.GET.get('sector_code', None)
    
    # 디버깅을 위한 출력
    print(f"API 키: {API_KEY}")
    print(f"선택된 권역코드: {selected_sector}")
    
    url = 'https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json'
    
    all_products_count = 0
    all_base_list = []
    all_option_list = []
    
    # 선택된 권역이 있으면 해당 권역만 조회, 없으면 모든 권역 조회
    sectors_to_query = [selected_sector] if selected_sector else SECTOR_CODES.keys()
    
    try:
        for sector_code in sectors_to_query:
            params = {
                'auth': API_KEY,
                'topFinGrpNo': sector_code,
                'pageNo': 1
            }
            
            # 응답 받기
            print(f"권역 {sector_code} ({SECTOR_CODES.get(sector_code, '알 수 없음')}) 조회 중...")
            response = requests.get(url, params=params, timeout=10)
            print(f"API 응답 상태 코드: {response.status_code}")
            
            # 상태 코드가 200이 아니면 다음 권역으로 진행
            if response.status_code != 200:
                print(f"권역 {sector_code} API 응답 오류: {response.text}")
                continue
            
            # JSON 파싱
            data = response.json()
            
            if 'result' not in data:
                print(f"권역 {sector_code} API 응답에 'result' 키가 없음")
                continue
                
            # 기본 정보 리스트
            base_list = data.get('result', {}).get('baseList', [])
            print(f"권역 {sector_code} baseList 길이: {len(base_list)}")
            
            # 옵션 정보 리스트
            option_list = data.get('result', {}).get('optionList', [])
            print(f"권역 {sector_code} optionList 길이: {len(option_list)}")
            
            # 결과 누적
            all_base_list.extend(base_list)
            all_option_list.extend(option_list)
            all_products_count += len(base_list)
            
            # 권역 정보를 각 상품에 추가
            for item in base_list:
                item['sector_code'] = sector_code
                item['sector_name'] = SECTOR_CODES.get(sector_code, '기타')
        
        # 은행 정보 저장
        for bank_data in all_base_list:
            bank, created = Bank.objects.get_or_create(
                fin_co_no=bank_data.get('fin_co_no'),
                defaults={
                    'kor_co_nm': bank_data.get('kor_co_nm'),
                    'sector_code': bank_data.get('sector_code', ''),
                    'sector_name': bank_data.get('sector_name', '')
                }
            )
            
            # 기존 은행 정보에 권역코드 업데이트
            if not created and (not bank.sector_code or not bank.sector_name):
                bank.sector_code = bank_data.get('sector_code', '')
                bank.sector_name = bank_data.get('sector_name', '')
                bank.save()
        
        # 상품별 옵션을 그룹화
        opts_by_product = {}
        for opt in all_option_list:
            prdt_cd = opt.get('fin_prdt_cd')
            if prdt_cd not in opts_by_product:
                opts_by_product[prdt_cd] = []
            opts_by_product[prdt_cd].append(opt)
        
        # 상품 정보 저장
        for product_data in all_base_list:
            try:
                bank = Bank.objects.get(fin_co_no=product_data.get('fin_co_no'))
                
                product, created = DepositProduct.objects.get_or_create(
                    fin_prdt_cd=product_data.get('fin_prdt_cd'),
                    defaults={
                        'bank': bank,
                        'fin_prdt_nm': product_data.get('fin_prdt_nm', ''),
                        'join_way': product_data.get('join_way', ''),
                        'mtrt_int': product_data.get('mtrt_int', ''),
                        'spcl_cnd': product_data.get('spcl_cnd', ''),
                        'dcls_month': product_data.get('dcls_month', ''),
                        'sector_code': product_data.get('sector_code', ''),
                    }
                )
                
                # 이미 존재하는 상품이면 정보 업데이트
                if not created:
                    product.fin_prdt_nm = product_data.get('fin_prdt_nm', '')
                    product.join_way = product_data.get('join_way', '')
                    product.mtrt_int = product_data.get('mtrt_int', '')
                    product.spcl_cnd = product_data.get('spcl_cnd', '')
                    product.dcls_month = product_data.get('dcls_month', '')
                    product.sector_code = product_data.get('sector_code', '')
                    
                # 금리 정보 저장
                prdt_cd = product_data.get('fin_prdt_cd')
                if prdt_cd in opts_by_product:
                    opt_list = opts_by_product[prdt_cd]
                    product.etc = opt_list
                    
                    # 최대 금리 계산
                    if opt_list:
                        # 금리 값이 누락된 경우를 처리
                        max_rate = 0
                        for opt in opt_list:
                            rate_str = opt.get('intr_rate', '0')
                            try:
                                rate = float(rate_str) if rate_str else 0
                                max_rate = max(max_rate, rate)
                            except ValueError:
                                print(f"금리 변환 오류: '{rate_str}'")
                        
                        product.max_rate = max_rate
                    
                    product.save()
            except Exception as e:
                print(f"상품 저장 중 오류: {str(e)}")
                # 개별 상품 오류는 건너뛰고 계속 진행
        
        return Response({
            "message": "정기예금 상품 정보를 성공적으로 저장했습니다.",
            "count": all_products_count
        })
        
    except requests.exceptions.RequestException as e:
        # 네트워크/요청 관련 예외 처리
        print(f"API 요청 오류: {str(e)}")
        return Response(
            {"error": f"API 요청 오류: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        # 기타 예외 처리 및 상세 로그 출력
        print(f"예외 발생: {str(e)}")
        traceback.print_exc()
        return Response(
            {"error": f"서버 오류: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 권역코드 목록 조회 API
@api_view(['GET'])
@permission_classes([AllowAny])  # 명시적으로 모든 사용자 접근 허용
def get_sectors(request):
    return Response(SECTOR_CODES)

# 은행 목록 조회 API
class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [AllowAny]  # 명시적으로 모든 사용자 접근 허용

# 예금 상품 목록 조회 API
class DepositProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    permission_classes = [AllowAny]  # 명시적으로 모든 사용자 접근 허용

    def get_queryset(self):
        queryset = DepositProduct.objects.all()
        
        # 권역코드 필터링
        sector_code = self.request.query_params.get('sector_code', None)
        if sector_code:
            queryset = queryset.filter(sector_code=sector_code)
            
        return queryset

# 가입하기 API 수정
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_deposit(request, pk):
    """정기예금 상품 가입하기"""
    try:
        deposit = DepositProduct.objects.get(pk=pk)
        user = request.user
        
        # 로그 추가
        print(f"사용자 {user.username}가 상품 ID {pk} 가입 시도")
        print(f"인증 헤더: {request.headers.get('Authorization')}")
        
        # 이미 가입한 상품인지 확인
        if user.subscribed_deposits.filter(pk=pk).exists():
            print(f"사용자 {user.username}는 이미 상품 ID {pk}에 가입되어 있음")
            return Response(
                {"message": "이미 가입한 상품입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 가입 처리
        user.subscribed_deposits.add(deposit)
        print(f"사용자 {user.username}가 상품 ID {pk}에 성공적으로 가입함")
        
        return Response({
            "message": f"{deposit.fin_prdt_nm} 상품에 가입되었습니다.",
            "product_id": pk,
            "product_name": deposit.fin_prdt_nm
        })
    except DepositProduct.DoesNotExist:
        print(f"상품 ID {pk}를 찾을 수 없음")
        return Response(
            {"error": "상품을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"가입 처리 중 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"가입 처리 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_subscription(request, pk):
    """사용자가 해당 상품에 가입했는지 확인"""
    try:
        is_subscribed = request.user.subscribed_deposits.filter(pk=pk).exists()
        return Response({
            "is_subscribed": is_subscribed
        })
    except Exception as e:
        return Response(
            {"error": f"가입 확인 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )