from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    작성자만 객체를 편집할 수 있도록 하는 권한 클래스
    """
    def has_object_permission(self, request, view, obj):
        # 디버깅 출력 추가
        print(f"권한 확인: {request.method}")
        print(f"현재 사용자: {request.user}, 인증 여부: {request.user.is_authenticated}")
        print(f"객체 작성자: {obj.author}")
        print(f"일치 여부: {obj.author == request.user}")
        
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 객체의 작성자에게만 허용
        return obj.author == request.user