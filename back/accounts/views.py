from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserDetailSerializer, UserSerializer, UserProfileUpdateSerializer, SignUpSerializer
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
import pandas as pd
import numpy as np
from deposits.models import DepositProduct, SavingProduct, DepositSubscription, SavingSubscription
import json

# 기존 함수들을 모두 유지하고 누락된 함수들만 추가

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """마이 프로필 조회"""
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """프로필 조회 및 수정"""
    if request.method == 'GET':
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """프로필 업데이트"""
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'user': UserDetailSerializer(request.user).data,
            'message': '프로필이 업데이트되었습니다.'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """사용자 프로필 정보 업데이트 (나이, 자산, 연봉)"""
    user = request.user
    
    data = request.data
    
    # 받은 데이터로 사용자 정보 업데이트
    if 'age' in data:
        user.age = data.get('age')
    if 'assets' in data:
        user.assets = data.get('assets')
    if 'annual_income' in data:
        user.annual_income = data.get('annual_income')
    if 'savings_tendency' in data:
        user.savings_tendency = data.get('savings_tendency')
    if 'investment_tendency' in data:
        user.investment_tendency = data.get('investment_tendency')
    if 'preferred_bank' in data:
        user.preferred_bank = data.get('preferred_bank')
    
    user.save()
    
    # 업데이트된 사용자 정보를 반환
    serializer = UserDetailSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """회원가입"""
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': '회원가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username is None or password is None:
        return Response({'error': '아이디와 비밀번호를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({'message': '로그인 성공'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': '로그아웃 완료'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """사용자 정보 조회"""
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

# YouTube 영상 저장 및 조회
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def youtube_videos(request):
    user = request.user
    
    if request.method == 'GET':
        # 사용자의 저장된 영상 목록을 반환
        return Response(user.saved_videos)
    
    elif request.method == 'POST':
        # 새 영상 저장
        video_data = request.data
        if not video_data:
            return Response({"error": "영상 데이터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 중복 체크를 위한 video_id 추출
        video_id = None
        if 'id' in video_data:
            if isinstance(video_data['id'], dict) and 'videoId' in video_data['id']:
                video_id = video_data['id']['videoId']
            elif isinstance(video_data['id'], str):
                video_id = video_data['id']
        
        if not video_id:
            return Response({"error": "유효한 영상 ID가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 중복 체크
        saved_videos = user.saved_videos or []
        
        # 이미 저장된 영상인지 확인
        for video in saved_videos:
            existing_id = None
            if 'id' in video:
                if isinstance(video['id'], dict) and 'videoId' in video['id']:
                    existing_id = video['id']['videoId']
                elif isinstance(video['id'], str):
                    existing_id = video['id']
            
            if existing_id == video_id:
                return Response({"message": "이미 저장된 영상입니다."}, status=status.HTTP_200_OK)
        
        # 새 영상 추가
        saved_videos.append(video_data)
        user.saved_videos = saved_videos
        user.save()
        
        return Response({"message": "영상이 저장되었습니다.", "video": video_data}, status=status.HTTP_201_CREATED)

# YouTube 채널 저장 및 조회
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def youtube_channels(request):
    user = request.user
    
    if request.method == 'GET':
        # 사용자의 저장된 채널 목록을 반환
        return Response(user.saved_channels)
    
    elif request.method == 'POST':
        # 새 채널 저장
        channel_data = request.data
        if not channel_data or not ('id' in channel_data or 'snippet' in channel_data):
            return Response({"error": "채널 데이터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        channel_id = None
        channel_title = None
        
        # snippet에서 채널 정보 추출
        if 'snippet' in channel_data:
            if 'channelId' in channel_data['snippet']:
                channel_id = channel_data['snippet']['channelId']
            if 'channelTitle' in channel_data['snippet']:
                channel_title = channel_data['snippet']['channelTitle']
        
        # 직접 입력된 채널 ID와 제목 사용
        if 'id' in channel_data and isinstance(channel_data['id'], str):
            channel_id = channel_data['id']
        if 'title' in channel_data and isinstance(channel_data['title'], str):
            channel_title = channel_data['title']
        
        if not channel_id or not channel_title:
            return Response({"error": "채널 ID와 이름이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 중복 체크
        saved_channels = user.saved_channels or []
        
        # 이미 저장된 채널인지 확인
        for channel in saved_channels:
            if 'id' in channel and channel['id'] == channel_id:
                return Response({"message": "이미 저장된 채널입니다."}, status=status.HTTP_200_OK)
        
        # 새 채널 추가 (간소화된 형태로 저장)
        new_channel = {
            "id": channel_id,
            "title": channel_title
        }
        saved_channels.append(new_channel)
        user.saved_channels = saved_channels
        user.save()
        
        return Response({"message": "채널이 저장되었습니다.", "channel": new_channel}, status=status.HTTP_201_CREATED)

# 특정 YouTube 영상 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def youtube_video_detail(request, video_id):
    user = request.user
    saved_videos = user.saved_videos or []
    
    # 기존 영상 검색
    updated_videos = []
    found = False
    
    for video in saved_videos:
        existing_id = None
        if 'id' in video:
            if isinstance(video['id'], dict) and 'videoId' in video['id']:
                existing_id = video['id']['videoId']
            elif isinstance(video['id'], str):
                existing_id = video['id']
                
        # 삭제할 video_id와 일치하지 않는 영상만 유지
        if existing_id != video_id:
            updated_videos.append(video)
        else:
            found = True
    
    if not found:
        return Response({"error": "해당 영상을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    # 업데이트된 영상 목록 저장
    user.saved_videos = updated_videos
    user.save()
    
    return Response({"message": "영상이 삭제되었습니다."}, status=status.HTTP_200_OK)

# 특정 YouTube 채널 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def youtube_channel_detail(request, channel_id):
    user = request.user
    saved_channels = user.saved_channels or []
    
    # 기존 채널 검색 및 삭제
    updated_channels = []
    found = False
    
    for channel in saved_channels:
        if channel.get('id') != channel_id:
            updated_channels.append(channel)
        else:
            found = True
    
    if not found:
        return Response({"error": "해당 채널을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    # 업데이트된 채널 목록 저장
    user.saved_channels = updated_channels
    user.save()
    
    return Response({"message": "채널이 삭제되었습니다."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_recommendations(request):
    """사용자와 유사한 프로필을 가진 사용자들이 가입한 상품 추천"""
    try:
        current_user = request.user
        
        # 현재 사용자의 프로필 정보 확인
        if not all([current_user.age, current_user.assets, current_user.annual_income]):
            return Response({
                'error': '추천을 받으려면 먼저 나이, 자산, 연봉 정보를 입력해주세요.',
                'recommendations': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 모든 사용자 데이터 가져오기 (현재 사용자 제외)
        users_data = User.objects.exclude(id=current_user.id).filter(
            age__isnull=False,
            assets__isnull=False,
            annual_income__isnull=False
        ).values(
            'id', 'age', 'assets', 'annual_income', 
            'savings_tendency', 'investment_tendency'
        )
        
        if not users_data:
            return Response({
                'message': '추천할 데이터가 부족합니다.',
                'recommendations': []
            })
        
        # pandas DataFrame으로 변환
        df = pd.DataFrame(list(users_data))
        
        # 현재 사용자 정보
        current_age = current_user.age
        current_assets = current_user.assets
        current_income = current_user.annual_income
        
        # 정규화를 위한 스케일링
        age_range = df['age'].max() - df['age'].min()
        assets_range = df['assets'].max() - df['assets'].min()
        income_range = df['annual_income'].max() - df['annual_income'].min()
        
        df['age_norm'] = (df['age'] - df['age'].min()) / age_range if age_range != 0 else 0
        df['assets_norm'] = (df['assets'] - df['assets'].min()) / assets_range if assets_range != 0 else 0
        df['income_norm'] = (df['annual_income'] - df['annual_income'].min()) / income_range if income_range != 0 else 0
        
        # 현재 사용자 정규화
        current_age_norm = (current_age - df['age'].min()) / age_range if age_range != 0 else 0
        current_assets_norm = (current_assets - df['assets'].min()) / assets_range if assets_range != 0 else 0
        current_income_norm = (current_income - df['annual_income'].min()) / income_range if income_range != 0 else 0
        
        # 유클리드 거리 계산 (가중치 적용)
        weights = {'age': 0.2, 'assets': 0.4, 'income': 0.4}  # 자산과 소득에 더 높은 가중치
        
        df['similarity_score'] = np.sqrt(
            weights['age'] * (df['age_norm'] - current_age_norm) ** 2 +
            weights['assets'] * (df['assets_norm'] - current_assets_norm) ** 2 +
            weights['income'] * (df['income_norm'] - current_income_norm) ** 2
        )
        
        # 가장 유사한 상위 50명 선택
        similar_users = df.nsmallest(50, 'similarity_score')['id'].tolist()
        
        # 현재 사용자가 이미 가입한 상품 ID 가져오기
        user_deposit_ids = set(
            DepositSubscription.objects.filter(user=current_user).values_list('product_id', flat=True)
        )
        user_saving_ids = set(
            SavingSubscription.objects.filter(user=current_user).values_list('product_id', flat=True)
        )
        
        # 유사한 사용자들이 가입한 상품 집계
        deposit_recommendations = {}
        saving_recommendations = {}
        
        # 예금 상품 집계
        deposit_subs = DepositSubscription.objects.filter(
            user_id__in=similar_users
        ).exclude(
            product_id__in=user_deposit_ids  # 이미 가입한 상품 제외
        ).values('product_id').annotate(
            count=Count('product_id')
        ).order_by('-count')
        
        for sub in deposit_subs:
            deposit_recommendations[sub['product_id']] = sub['count']
        
        # 적금 상품 집계
        saving_subs = SavingSubscription.objects.filter(
            user_id__in=similar_users
        ).exclude(
            product_id__in=user_saving_ids  # 이미 가입한 상품 제외
        ).values('product_id').annotate(
            count=Count('product_id')
        ).order_by('-count')
        
        for sub in saving_subs:
            saving_recommendations[sub['product_id']] = sub['count']
        
        # 추천 상품 상세 정보 가져오기
        recommended_deposits = []
        recommended_savings = []
        
        # 상위 5개 예금 상품
        top_deposit_ids = list(deposit_recommendations.keys())[:5]
        if top_deposit_ids:
            deposit_products = DepositProduct.objects.filter(
                fin_prdt_cd__in=top_deposit_ids
            ).select_related('bank')
            
            for product in deposit_products:
                # options 데이터 파싱
                options_data = []
                if product.options:
                    if isinstance(product.options, str):
                        try:
                            options_data = json.loads(product.options)
                        except json.JSONDecodeError:
                            options_data = []
                    elif isinstance(product.options, list):
                        options_data = product.options
                
                product_data = {
                    'product': {
                        'fin_prdt_cd': product.fin_prdt_cd,
                        'fin_prdt_nm': product.fin_prdt_nm,
                        'bank': {
                            'kor_co_nm': product.bank.kor_co_nm if product.bank else '정보 없음'
                        },
                        'options': options_data
                    },
                    'recommendation_count': deposit_recommendations[product.fin_prdt_cd],
                    'type': 'deposit'
                }
                recommended_deposits.append(product_data)
        
        # 상위 5개 적금 상품
        top_saving_ids = list(saving_recommendations.keys())[:5]
        if top_saving_ids:
            saving_products = SavingProduct.objects.filter(
                fin_prdt_cd__in=top_saving_ids
            ).select_related('bank')
            
            for product in saving_products:
                # options 데이터 파싱
                options_data = []
                if product.options:
                    if isinstance(product.options, str):
                        try:
                            options_data = json.loads(product.options)
                        except json.JSONDecodeError:
                            options_data = []
                    elif isinstance(product.options, list):
                        options_data = product.options
                
                product_data = {
                    'product': {
                        'fin_prdt_cd': product.fin_prdt_cd,
                        'fin_prdt_nm': product.fin_prdt_nm,
                        'bank': {
                            'kor_co_nm': product.bank.kor_co_nm if product.bank else '정보 없음'
                        },
                        'options': options_data
                    },
                    'recommendation_count': saving_recommendations[product.fin_prdt_cd],
                    'type': 'saving'
                }
                recommended_savings.append(product_data)
        
        # 추천 점수 순으로 정렬
        recommended_deposits.sort(key=lambda x: x['recommendation_count'], reverse=True)
        recommended_savings.sort(key=lambda x: x['recommendation_count'], reverse=True)
        
        # 전체 추천 결과 합치기 (최대 10개)
        all_recommendations = recommended_deposits + recommended_savings
        all_recommendations.sort(key=lambda x: x['recommendation_count'], reverse=True)
        
        return Response({
            'message': f'{len(similar_users)}명의 유사한 사용자 데이터를 기반으로 추천합니다.',
            'recommendations': all_recommendations[:10],
            'similar_users_count': len(similar_users)
        })
        
    except Exception as e:
        print(f'상품 추천 중 오류 발생: {str(e)}')
        import traceback
        traceback.print_exc()
        return Response({
            'error': '상품 추천 중 오류가 발생했습니다.',
            'recommendations': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)