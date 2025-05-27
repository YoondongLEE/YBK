from rest_framework import serializers
from .models import Question, Choice, QuestionCategory, UserQuizAttempt, UserAnswer

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'keywords', 'explanation', 'choices', 'difficulty']

class QuestionForQuizSerializer(serializers.ModelSerializer):
    """퀴즈용 시리얼라이저 - 정답 숨김"""
    choices = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'keywords', 'choices']
    
    def get_choices(self, obj):
        choices = obj.choices.all()
        return [{'id': choice.id, 'text': choice.text} for choice in choices]

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['question', 'selected_choice', 'is_correct']

class UserQuizAttemptSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserQuizAttempt
        fields = ['id', 'difficulty', 'score', 'total_questions', 'correct_answers', 'completed_at', 'answers']