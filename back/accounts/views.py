from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserDetailSerializer

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