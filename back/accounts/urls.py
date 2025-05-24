from django.urls import path
from . import views

urlpatterns = [
    # 기존 URL 패턴들
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.get_user_info, name='user_info'),
    
    # 프로필 API 추가
    path('profile/', views.my_profile, name='my_profile'),
    
    # YouTube 영상 및 채널 관리 API
    path('youtube/videos/', views.youtube_videos, name='youtube_videos'),
    path('youtube/channels/', views.youtube_channels, name='youtube_channels'),
    path('youtube/videos/<str:video_id>/', views.youtube_video_detail, name='youtube_video_detail'),
    path('youtube/channels/<str:channel_id>/', views.youtube_channel_detail, name='youtube_channel_detail'),
]