from django.urls import path
from . import views

urlpatterns = [
    path('my-profile/', views.my_profile, name='my_profile'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user-info/', views.get_user_info, name='get_user_info'),
    path('youtube/videos/', views.youtube_videos, name='youtube_videos'),
    path('youtube/channels/', views.youtube_channels, name='youtube_channels'),
    path('youtube/videos/<str:video_id>/', views.youtube_video_detail, name='youtube_video_detail'),
    path('youtube/channels/<str:channel_id>/', views.youtube_channel_detail, name='youtube_channel_detail'),
]