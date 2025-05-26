from django.db import models
from django.conf import settings

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('경제뉴스', '경제뉴스'),
        ('투자정보', '투자정보'),
        ('자유게시판', '자유게시판'),
        ('질문답변', '질문답변'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='자유게시판')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # 이 필드는 있는데
    updated_at = models.DateTimeField(auto_now=True)      # 이 필드를 추가해야 함
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username}'s comment on {self.post.title}"