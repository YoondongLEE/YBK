from django.db import models
from django.conf import settings
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QuestionCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Question Categories"
    
    def __str__(self):
        return self.name

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('youth', '청소년'),
        ('adult_basic', '성인 기본'),
        ('adult_advanced', '성인 심화'),
    ]
    
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    text = models.TextField()
    keywords = models.JSONField(default=list)
    explanation = models.TextField()
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.text[:50]}..."

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.text} ({'정답' if self.is_correct else '오답'})"

class UserQuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20, choices=Question.DIFFICULTY_CHOICES)
    score = models.IntegerField()  # 점수 (0-100)
    total_questions = models.IntegerField(default=10)
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_difficulty_display()} ({self.score}점)"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserQuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    
    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.id} ({'O' if self.is_correct else 'X'})"

# 새로 추가되는 Assessment 모델
class Assessment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessments')
    difficulty = models.CharField(max_length=20, choices=Question.DIFFICULTY_CHOICES)
    score = models.IntegerField()  # 맞춘 개수 (0-10)
    grade = models.CharField(max_length=5)  # AH, AM, AL, IH, IM, IL, NH, NM, NL
    total_questions = models.IntegerField(default=10)
    passed = models.BooleanField()  # 60점 이상 합격 여부
    questions_data = models.JSONField()  # 출제된 문제들과 정답
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_difficulty_display()} - {self.grade} ({self.score}/10)"
    
    @property
    def score_percentage(self):
        return (self.score / self.total_questions) * 100

# 수료증 모델 추가
class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    difficulty = models.CharField(max_length=20, choices=Question.DIFFICULTY_CHOICES)
    certificate_number = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=5)  # AH, AM, AL, IH, IM, IL, NH, NM, NL
    score = models.IntegerField()
    total_questions = models.IntegerField(default=10)
    file_path = models.CharField(max_length=500)  # 수료증 이미지 파일 경로
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'difficulty']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.difficulty} - {self.grade}"
    
    @property
    def score_percentage(self):
        return (self.score / self.total_questions) * 100
    
    @classmethod
    def generate_certificate_number(cls):
        """발급번호 생성: 제 2025-0001 형식"""
        current_year = timezone.now().year
        year_certificates = cls.objects.filter(
            created_at__year=current_year
        ).count()
        return f"{current_year}-{year_certificates + 1:03d}"
    
    @staticmethod
    def calculate_grade(difficulty, score_percentage):
        """난이도별 등급 계산"""
        if score_percentage < 60:
            return None  # 불합격
        
        if score_percentage >= 90:
            if difficulty == 'adult_advanced':
                return 'AH'
            elif difficulty == 'adult_basic':
                return 'IH'
            else:  # youth
                return 'NH'
        elif score_percentage >= 75:
            if difficulty == 'adult_advanced':
                return 'AM'
            elif difficulty == 'adult_basic':
                return 'IM'
            else:  # youth
                return 'NM'
        elif score_percentage >= 60:
            if difficulty == 'adult_advanced':
                return 'AL'
            elif difficulty == 'adult_basic':
                return 'IL'
            else:  # youth
                return 'NL'
        
        return None