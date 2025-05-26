import os
import requests
import traceback
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

# 모델 import 추가
from .models import Bank, DepositProduct, DepositOption, DepositSubscription, SavingProduct, SavingOption, SavingSubscription
# 시리얼라이저 import 추가
from .serializers import BankSerializer, DepositProductSerializer, SavingProductSerializer

from .models import DepositSubscription, SavingSubscription

# .env 파일에서 API 키 가져오기
API_KEY = os.environ.get('FINLIFE_API_KEY')

# API 키가 없을 경우 오류 로그
if not API_KEY:
    print("경고: FINLIFE_API_KEY 환경변수가 설정되어 있지 않습니다.")

# 권역코드 정의
SECTOR_CODES = {
    '020000': '은행',
    '030200': '여신전문',
    '030300': '저축은행',
    '050000': '보험',
    '060000': '금융투자'
}

@api_view(['GET'])
@permission_classes([AllowAny])
def save_deposit_products(request):
    """금융감독원 API에서 정기예금 상품 정보를 가져와 DB에 저장"""
    
    # 강제 새로고침 여부 확인
    force_refresh = request.GET.get('force_refresh', 'false').lower() == 'true'

    # 이미 데이터가 있는지 확인
    existing_products_count = DepositProduct.objects.count()
    
    # 데이터가 이미 있으면 API 호출 스킵
    if existing_products_count > 0 and not force_refresh:
        return Response({
            "message": f"이미 {existing_products_count}개의 정기예금 상품 정보가 저장되어 있습니다.",
            "count": existing_products_count,
            "refresh": False
        })
    
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
        # 각 권역별로 API 호출
        for sector_code in sectors_to_query:
            params = {
                'auth': API_KEY,
                'topFinGrpNo': sector_code,
                'pageNo': 1
            }
            
            # API 요청
            response = requests.get(url, params=params)
            response.raise_for_status()  # HTTP 오류 발생시 예외 발생
            
            data = response.json()
            
            # 기준 정보 및 옵션 정보 추출
            base_list = data.get('result', {}).get('baseList', [])
            option_list = data.get('result', {}).get('optionList', [])
            
            # 결과 합치기
            all_base_list.extend(base_list)
            all_option_list.extend(option_list)
            
            # 은행 정보 저장
            for item in base_list:
                bank_data = {
                    'fin_co_no': item.get('fin_co_no', ''),
                    'kor_co_nm': item.get('kor_co_nm', ''),
                    'sector_code': sector_code,
                    'sector_name': SECTOR_CODES.get(sector_code, '')
                }
                
                # 은행 저장 또는 업데이트
                bank, created = Bank.objects.update_or_create(
                    fin_co_no=bank_data['fin_co_no'],
                    defaults=bank_data
                )
                
                # 상품 정보 저장
                product_data = {
                    'bank': bank,
                    'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                    'join_way': item.get('join_way', ''),
                    'mtrt_int': item.get('mtrt_int', ''),
                    'spcl_cnd': item.get('spcl_cnd', ''),
                    'join_member': item.get('join_member', ''),
                    'join_deny': item.get('join_deny', ''),
                    'etc_note': item.get('etc_note', ''),
                    'max_limit': int(item.get('max_limit', 0)) if item.get('max_limit') else None,
                    'dcls_strt_day': item.get('dcls_strt_day', ''),
                    'dcls_end_day': item.get('dcls_end_day', ''),
                    'fin_co_subm_day': item.get('fin_co_subm_day', ''),
                    'sector_code': sector_code,
                }
                
                # 해당 상품의 옵션 필터링
                product_options = [opt for opt in option_list if opt.get('fin_prdt_cd') == item.get('fin_prdt_cd')]
                product_data['options'] = product_options
                
                # 상품 저장 또는 업데이트
                product, created = DepositProduct.objects.update_or_create(
                    fin_prdt_cd=item.get('fin_prdt_cd', ''),
                    defaults=product_data
                )
                
                all_products_count += 1
        
        return Response({
            "message": "정기예금 상품 정보를 성공적으로 저장했습니다.",
            "count": all_products_count,
            "refresh": True
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
    """정기예금 상품 가입 또는 취소하기"""
    try:
        deposit = DepositProduct.objects.get(pk=pk)
        user = request.user
        
        # 요청 본문을 확인하여 취소 요청인지 확인
        is_unsubscribe = request.data.get('action') == 'unsubscribe'
        
        # 이미 가입한 상품인지 확인
        is_subscribed = user.subscribed_deposits.filter(pk=pk).exists()
        
        # 로그 추가
        print(f"사용자 {user.username}가 상품 ID {pk} {'취소' if is_unsubscribe else '가입'} 시도")
        
        # 가입 취소 요청이면
        if is_unsubscribe:
            if is_subscribed:
                user.subscribed_deposits.remove(deposit)
                print(f"사용자 {user.username}가 상품 ID {pk} 가입 취소 완료")
                return Response({
                    "message": f"{deposit.fin_prdt_nm} 상품 가입이 취소되었습니다.",
                    "is_subscribed": False
                })
            else:
                return Response({
                    "message": "가입되지 않은 상품입니다.",
                    "is_subscribed": False
                })
        
        # 가입 요청이면
        else:
            if is_subscribed:
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
                "product_name": deposit.fin_prdt_nm,
                "is_subscribed": True
            })
            
    except DepositProduct.DoesNotExist:
        print(f"상품 ID {pk}를 찾을 수 없음")
        return Response(
            {"error": "상품을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"가입/취소 처리 중 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"가입/취소 처리 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_subscription(request, pk):
    """사용자가 해당 상품에 가입했는지 확인"""
    try:
        is_subscribed = request.user.subscribed_deposits.filter(pk=pk).exists()  # subscribed_deposits 필드 사용
        return Response({
            "is_subscribed": is_subscribed
        })
    except Exception as e:
        return Response(
            {"error": f"가입 확인 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# 적금 상품 목록 조회 API
class SavingProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SavingProduct.objects.all()
    serializer_class = SavingProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = SavingProduct.objects.all()
        
        # 권역코드 필터링
        sector_code = self.request.query_params.get('sector_code', None)
        if sector_code:
            queryset = queryset.filter(sector_code=sector_code)
            
        return queryset

# 적금 상품 정보 가져오기
@api_view(['GET'])
@permission_classes([AllowAny])
def save_saving_products(request):
    """금융감독원 API에서 정기적금 상품 정보를 가져와 DB에 저장"""

    # 강제 새로고침 여부 확인
    force_refresh = request.GET.get('force_refresh', 'false').lower() == 'true'
    
    # 이미 데이터가 있는지 확인
    existing_products_count = SavingProduct.objects.count()
    
    # 데이터가 이미 있으면 API 호출 스킵
    if existing_products_count > 0 and not force_refresh:
        return Response({
            "message": f"이미 {existing_products_count}개의 정기적금 상품 정보가 저장되어 있습니다.",
            "count": existing_products_count,
            "refresh": False
        })
    
    # 권역코드 파라미터 가져오기 (기본값: 모든 권역)
    selected_sector = request.GET.get('sector_code', None)
    
    # 디버깅을 위한 출력
    print(f"API 키: {API_KEY}")
    print(f"선택된 권역코드: {selected_sector}")
    
    url = 'https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json'
    
    all_products_count = 0
    all_base_list = []
    all_option_list = []
    
    # 선택된 권역이 있으면 해당 권역만 조회, 없으면 모든 권역 조회
    sectors_to_query = [selected_sector] if selected_sector else SECTOR_CODES.keys()
    
    try:
        # 각 권역별로 API 호출
        for sector_code in sectors_to_query:
            params = {
                'auth': API_KEY,
                'topFinGrpNo': sector_code,
                'pageNo': 1
            }
            
            # API 요청
            response = requests.get(url, params=params)
            response.raise_for_status()  # HTTP 오류 발생시 예외 발생
            
            data = response.json()
            
            # 기준 정보 및 옵션 정보 추출
            base_list = data.get('result', {}).get('baseList', [])
            option_list = data.get('result', {}).get('optionList', [])
            
            # 결과 합치기
            all_base_list.extend(base_list)
            all_option_list.extend(option_list)
            
            # 은행 정보 저장
            for item in base_list:
                bank_data = {
                    'fin_co_no': item.get('fin_co_no', ''),
                    'kor_co_nm': item.get('kor_co_nm', ''),
                    'sector_code': sector_code,
                    'sector_name': SECTOR_CODES.get(sector_code, '')
                }
                
                # 은행 저장 또는 업데이트
                bank, created = Bank.objects.update_or_create(
                    fin_co_no=bank_data['fin_co_no'],
                    defaults=bank_data
                )
                
                # 상품 정보 저장
                product_data = {
                    'bank': bank,
                    'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                    'join_way': item.get('join_way', ''),
                    'mtrt_int': item.get('mtrt_int', ''),
                    'spcl_cnd': item.get('spcl_cnd', ''),
                    'join_member': item.get('join_member', ''),
                    'join_deny': item.get('join_deny', ''),
                    'etc_note': item.get('etc_note', ''),
                    'max_limit': int(item.get('max_limit', 0)) if item.get('max_limit') else None,
                    'dcls_strt_day': item.get('dcls_strt_day', ''),
                    'dcls_end_day': item.get('dcls_end_day', ''),
                    'fin_co_subm_day': item.get('fin_co_subm_day', ''),
                    'sector_code': sector_code,
                }
                
                # 해당 상품의 옵션 필터링
                product_options = [opt for opt in option_list if opt.get('fin_prdt_cd') == item.get('fin_prdt_cd')]
                product_data['options'] = product_options
                
                # 상품 저장 또는 업데이트 - SavingProduct 모델 사용
                product, created = SavingProduct.objects.update_or_create(
                    fin_prdt_cd=item.get('fin_prdt_cd', ''),
                    defaults=product_data
                )
                
                all_products_count += 1
        
        return Response({
            "message": "정기적금 상품 정보를 성공적으로 저장했습니다.",
            "count": all_products_count,
            "refresh": True
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

# 적금 상품 가입하기
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_saving(request, pk):
    """정기적금 상품 가입 또는 취소하기"""
    try:
        saving = SavingProduct.objects.get(pk=pk)
        user = request.user
        
        # 요청 본문을 확인하여 취소 요청인지 확인
        is_unsubscribe = request.data.get('action') == 'unsubscribe'
        
        # 이미 가입한 상품인지 확인
        is_subscribed = user.subscribed_savings.filter(pk=pk).exists()
        
        # 로그 추가
        print(f"사용자 {user.username}가 상품 ID {pk} {'취소' if is_unsubscribe else '가입'} 시도")
        
        # 가입 취소 요청이면
        if is_unsubscribe:
            if is_subscribed:
                user.subscribed_savings.remove(saving)
                print(f"사용자 {user.username}가 상품 ID {pk} 가입 취소 완료")
                return Response({
                    "message": f"{saving.fin_prdt_nm} 상품 가입이 취소되었습니다.",
                    "is_subscribed": False
                })
            else:
                return Response({
                    "message": "가입되지 않은 상품입니다.",
                    "is_subscribed": False
                })
        
        # 가입 요청이면
        else:
            if is_subscribed:
                print(f"사용자 {user.username}는 이미 상품 ID {pk}에 가입되어 있음")
                return Response(
                    {"message": "이미 가입한 상품입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 가입 처리
            user.subscribed_savings.add(saving)
            print(f"사용자 {user.username}가 상품 ID {pk}에 성공적으로 가입함")
            
            return Response({
                "message": f"{saving.fin_prdt_nm} 상품에 가입되었습니다.",
                "product_id": pk,
                "product_name": saving.fin_prdt_nm,
                "is_subscribed": True
            })
            
    except SavingProduct.DoesNotExist:
        print(f"상품 ID {pk}를 찾을 수 없음")
        return Response(
            {"error": "상품을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"가입/취소 처리 중 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"가입/취소 처리 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_saving_subscription(request, pk):
    """사용자가 해당 적금 상품에 가입했는지 확인"""
    try:
        is_subscribed = request.user.subscribed_savings.filter(pk=pk).exists()  # subscribed_savings 필드 사용
        return Response({
            "is_subscribed": is_subscribed
        })
    except Exception as e:
        return Response(
            {"error": f"적금 가입 확인 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscribed_deposits(request):
    """사용자가 가입한 예금 상품 목록 조회"""
    user = request.user
    
    try:
        # DepositSubscription을 통해 가입한 상품 조회
        subscriptions = DepositSubscription.objects.filter(user=user).select_related('product__bank')
        subscribed_deposits = []
        
        for sub in subscriptions:
            product = sub.product
            
            # JSON 필드에서 options 데이터 가져오기
            options_data = []
            if product.options:
                if isinstance(product.options, str):
                    try:
                        options_data = json.loads(product.options)
                    except json.JSONDecodeError:
                        options_data = []
                elif isinstance(product.options, list):
                    options_data = product.options
            
            # 만약 JSONField의 options가 비어있으면 deposit_options 관계에서 가져오기
            if not options_data:
                options_data = list(product.deposit_options.all().values(
                    'intr_rate_type', 'intr_rate_type_nm', 'save_trm', 'intr_rate', 'intr_rate2'
                ))
            
            product_data = {
                'fin_prdt_cd': product.fin_prdt_cd,
                'fin_prdt_nm': product.fin_prdt_nm,
                'join_way': product.join_way,
                'mtrt_int': product.mtrt_int,
                'spcl_cnd': product.spcl_cnd,
                'join_member': product.join_member,
                'join_deny': product.join_deny,
                'etc_note': product.etc_note,
                'max_limit': product.max_limit,
                'dcls_strt_day': product.dcls_strt_day,
                'dcls_end_day': product.dcls_end_day,
                'fin_co_subm_day': product.fin_co_subm_day,
                'sector_code': product.sector_code,
                'bank': {
                    'fin_co_no': product.bank.fin_co_no,
                    'kor_co_nm': product.bank.kor_co_nm,
                    'sector_code': product.bank.sector_code,
                    'sector_name': product.bank.sector_name,
                },
                'options': options_data  # 파싱된 옵션 데이터
            }
            subscribed_deposits.append(product_data)
        
        print(f'예금 상품 조회 성공: {len(subscribed_deposits)}개')
        if subscribed_deposits and subscribed_deposits[0]['options']:
            print(f'첫 번째 상품 옵션 개수: {len(subscribed_deposits[0]["options"])}')
            print(f'첫 번째 옵션 데이터: {subscribed_deposits[0]["options"][0]}')
            
        return Response(subscribed_deposits, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f'예금 상품 조회 실패: {e}')
        import traceback
        traceback.print_exc()
        return Response(
            {'error': '예금 상품 조회에 실패했습니다.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscribed_savings(request):
    """사용자가 가입한 적금 상품 목록 조회"""
    user = request.user
    
    try:
        # SavingSubscription을 통해 가입한 상품 조회
        subscriptions = SavingSubscription.objects.filter(user=user).select_related('product__bank')
        subscribed_savings = []
        
        for sub in subscriptions:
            product = sub.product
            
            # JSON 필드에서 options 데이터 가져오기
            options_data = []
            if product.options:
                if isinstance(product.options, str):
                    try:
                        options_data = json.loads(product.options)
                    except json.JSONDecodeError:
                        options_data = []
                elif isinstance(product.options, list):
                    options_data = product.options
            
            # 만약 JSONField의 options가 비어있으면 saving_options 관계에서 가져오기
            if not options_data:
                options_data = list(product.saving_options.all().values(
                    'intr_rate_type', 'intr_rate_type_nm', 'save_trm', 'intr_rate', 'intr_rate2'
                ))
            
            product_data = {
                'fin_prdt_cd': product.fin_prdt_cd,
                'fin_prdt_nm': product.fin_prdt_nm,
                'join_way': product.join_way,
                'mtrt_int': product.mtrt_int,
                'spcl_cnd': product.spcl_cnd,
                'join_member': product.join_member,
                'join_deny': product.join_deny,
                'etc_note': product.etc_note,
                'max_limit': product.max_limit,
                'dcls_strt_day': product.dcls_strt_day,
                'dcls_end_day': product.dcls_end_day,
                'fin_co_subm_day': product.fin_co_subm_day,
                'sector_code': product.sector_code,
                'bank': {
                    'fin_co_no': product.bank.fin_co_no,
                    'kor_co_nm': product.bank.kor_co_nm,
                    'sector_code': product.bank.sector_code,
                    'sector_name': product.bank.sector_name,
                },
                'options': options_data  # 파싱된 옵션 데이터
            }
            subscribed_savings.append(product_data)
        
        print(f'적금 상품 조회 성공: {len(subscribed_savings)}개')
        if subscribed_savings and subscribed_savings[0]['options']:
            print(f'첫 번째 상품 옵션 개수: {len(subscribed_savings[0]["options"])}')
            print(f'첫 번째 옵션 데이터: {subscribed_savings[0]["options"][0]}')
            
        return Response(subscribed_savings, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f'적금 상품 조회 실패: {e}')
        import traceback
        traceback.print_exc()
        return Response(
            {'error': '적금 상품 조회에 실패했습니다.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )