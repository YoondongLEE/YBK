from django.urls import path
from . import views

urlpatterns = [
    # 기존 프로필 관련 URL들
    path('my-profile/', views.my_profile, name='my_profile'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # 기존 인증 관련 URL들
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user-info/', views.get_user_info, name='get_user_info'),
    
    # 기존 YouTube 관련 URL들
    path('youtube/videos/', views.youtube_videos, name='youtube_videos'),
    path('youtube/channels/', views.youtube_channels, name='youtube_channels'),
    path('youtube/videos/<str:video_id>/', views.youtube_video_detail, name='youtube_video_detail'),
    path('youtube/channels/<str:channel_id>/', views.youtube_channel_detail, name='youtube_channel_detail'),
    
    # 새로 추가된 추천 기능 URL
    path('recommendations/', views.get_product_recommendations, name='product-recommendations'),
]