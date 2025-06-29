from django.urls import path
from . import views

urlpatterns = [
    # 기존 퀴즈 관련 URL들 (그대로 유지)
    path('quiz/difficulties/', views.get_quiz_difficulties, name='quiz_difficulties'),
    path('quiz/<str:difficulty>/', views.get_quiz_questions, name='quiz_questions'),
    path('quiz/submit/', views.submit_quiz_answers, name='submit_quiz'),
    path('quiz/history/', views.get_user_quiz_history, name='quiz_history'),
    
    # 기존 학습용 URL들 (그대로 유지)
    path('questions/', views.question_list, name='question_list'),
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
    path('questions/<int:question_id>/submit/', views.submit_answer, name='submit_answer'),
    path('categories/', views.category_list, name='category_list'),
    
    # 기존 개념 학습용 URL들
    path('concept-study/<str:difficulty>/categories/', views.get_categories_by_difficulty, name='concept_categories'),
    path('concept-study/<str:difficulty>/category/<int:category_id>/', views.get_concept_study_questions, name='concept_study_questions'),
    
    # Assessment 관련 URL들
    path('assessment/start/', views.start_assessment, name='start_assessment'),
    path('assessment/submit/', views.submit_assessment, name='submit_assessment'),
    path('assessment/history/', views.assessment_history, name='assessment_history'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    
    # 수료증 관련 URL들 (새로 추가)
    path('certificate/generate/<int:assessment_id>/', views.generate_certificate, name='generate_certificate'),
    path('certificate/download/<int:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('certificates/', views.user_certificates, name='user_certificates'),
]