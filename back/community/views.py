from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    # 기본적으로 인증된 사용자만 쓰기 가능, 모든 사람이 읽기 가능
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer   # 이 부분이 꼭 있어야 합니다
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostDetailSerializer
    
    def get_queryset(self):
        try:
            queryset = Post.objects.all()
            print(f"게시글 수: {queryset.count()}")
            category = self.request.query_params.get('category')
            if category:
                queryset = queryset.filter(category=category)
            return queryset
        except Exception as e:
            import traceback
            print(f"게시글 목록 조회 오류: {str(e)}")
            print(traceback.format_exc())
            # 빈 쿼리셋이라도 반환
            return Post.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # 디버깅 출력 추가
        print(f"현재 요청 사용자: {self.request.user}")
        print(f"인증 여부: {self.request.user.is_authenticated}")
        return context

    def retrieve(self, request, *args, **kwargs):
        # 조회수 증가
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # POST /posts/ → PostCreateSerializer → 저장 → PostDetailSerializer 응답
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        out_serializer = PostDetailSerializer(post, context={'request': request})
        headers = self.get_success_headers(out_serializer.data)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        return Response({
            'liked': liked,
            'like_count': post.likes.count()
        })
    
    # 권한 로깅 추가
    def perform_update(self, serializer):
        print(f"수정 요청 - HTTP 메소드: {self.request.method}")
        print(f"헤더 정보: {self.request.headers}")
        print(f"현재 사용자: {self.request.user}, ID: {self.request.user.id}")
        print(f"게시글 작성자: {serializer.instance.author}, ID: {serializer.instance.author.id}")
        print(f"두 ID의 타입: {type(self.request.user.id)}, {type(serializer.instance.author.id)}")
        print(f"수정 권한 여부: {self.request.user.id == serializer.instance.author.id}")
        
        # 강제로 작성자와 동일한 경우에만 수정 허용
        if self.request.user.id != serializer.instance.author.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("이 게시글을 수정할 권한이 없습니다.")
        
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # 인증된 사용자만 쓰기 가능, 작성자만 수정/삭제 가능
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response({"error": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
