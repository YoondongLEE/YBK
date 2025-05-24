from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Min, Max, Avg
from datetime import datetime
from .models import FinanceInfo, MetalPrice
from .serializers import FinanceInfoSerializer, MetalPriceSerializer

class FinanceInfoViewSet(viewsets.ModelViewSet):
    queryset = FinanceInfo.objects.all()
    serializer_class = FinanceInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['GET'])
@permission_classes([AllowAny])
def get_metal_prices(request):
    """
    금/은 가격 데이터를 조회하는 API
    
    쿼리 파라미터:
    - metal_type: 'gold' 또는 'silver'
    - start_date: YYYY-MM-DD 형식의 시작일 (선택)
    - end_date: YYYY-MM-DD 형식의 종료일 (선택)
    """
    metal_type = request.query_params.get('metal_type', 'gold')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # 금속 유형 검증
    if metal_type not in ['gold', 'silver']:
        return Response(
            {"error": "Invalid metal type. Use 'gold' or 'silver'."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 기본 쿼리셋
    queryset = MetalPrice.objects.filter(metal_type=metal_type)
    
    # 날짜 필터 적용
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date_obj)
        except ValueError:
            return Response(
                {"error": "Invalid start_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(date__lte=end_date_obj)
        except ValueError:
            return Response(
                {"error": "Invalid end_date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # 데이터 직렬화
    serializer = MetalPriceSerializer(queryset, many=True)
    
    # 통계 정보 계산
    if queryset.exists():
        stats = queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price')
        )
        return Response({
            'data': serializer.data,
            'statistics': stats
        })
    
    return Response({
        'data': [],
        'statistics': {
            'min_price': 0,
            'max_price': 0,
            'avg_price': 0
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def load_metal_price_data(request):
    """
    관리자용 API: Excel 파일에서 금/은 가격 데이터를 DB에 로드
    """
    from django.core.management import call_command
    
    try:
        call_command('load_metal_prices')
        return Response({"message": "Metal price data loaded successfully"})
    except Exception as e:
        return Response(
            {"error": f"Failed to load data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )