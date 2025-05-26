from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserDetailSerializer, UserSerializer, UserProfileUpdateSerializer, SignUpSerializer
from django.contrib.auth import authenticate, login, logout


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """사용자 프로필 정보와 가입한 상품 목록 조회"""
    try:
        # 디버그 출력
        print(f"요청 헤더: {request.headers}")
        print(f"인증된 사용자: {request.user.username} ({request.user.id})")
        
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    except Exception as e:
        print(f"프로필 조회 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"프로필 정보를 조회하는 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """현재 로그인한 사용자의 프로필 정보를 반환"""
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """사용자 프로필 정보 업데이트 (나이, 자산, 연봉)"""
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # 업데이트된 전체 프로필 정보 반환
        updated_user = UserDetailSerializer(request.user)
        return Response(updated_user.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """회원가입"""
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_data = UserDetailSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "사용자 이름과 비밀번호를 모두 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({"message": "로그인 성공!"})
    else:
        return Response({"error": "사용자 이름 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "로그아웃 되었습니다."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    serializer = UserSerializer(user)
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
    
    return Response({"message": "영상이 삭제되었습니다."})


# 특정 YouTube 채널 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def youtube_channel_detail(request, channel_id):
    user = request.user
    saved_channels = user.saved_channels or []
    
    # 기존 채널 검색
    updated_channels = [channel for channel in saved_channels if channel.get('id') != channel_id]
    
    if len(updated_channels) == len(saved_channels):
        return Response({"error": "해당 채널을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    # 업데이트된 채널 목록 저장
    user.saved_channels = updated_channels
    user.save()
    
    return Response({"message": "채널이 삭제되었습니다."})