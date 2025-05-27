from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Question, Choice, UserQuizAttempt, UserAnswer, QuestionCategory
from .serializers import QuestionForQuizSerializer, UserQuizAttemptSerializer, QuestionSerializer
import random

@api_view(['GET'])
def get_quiz_questions(request, difficulty):
    """특정 난이도의 랜덤 10문제 제공 (선택지 순서 랜덤)"""
    try:
        # 해당 난이도의 모든 문제 가져오기
        all_questions = Question.objects.filter(difficulty=difficulty)
        
        if all_questions.count() < 10:
            return Response({
                'error': f'{difficulty} 난이도의 문제가 10개 미만입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 랜덤하게 10문제 선택
        random_questions = random.sample(list(all_questions), 10)
        
        # 각 문제의 선택지 순서를 랜덤하게 섞기
        questions_data = []
        for question in random_questions:
            # 선택지들을 가져와서 랜덤하게 섞기
            choices = list(question.choices.all())
            random.shuffle(choices)
            
            question_data = {
                'id': question.id,
                'text': question.text,
                'difficulty': question.difficulty,
                'explanation': question.explanation,
                'keywords': question.keywords,
                'choices': [
                    {
                        'id': choice.id,
                        'text': choice.text,
                        'is_correct': choice.is_correct
                    }
                    for choice in choices
                ]
            }
            questions_data.append(question_data)
        
        return Response({
            'questions': questions_data,
            'difficulty': difficulty,
            'total_questions': 10
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_answers(request):
    """퀴즈 답안 제출 및 채점"""
    try:
        user = request.user
        answers = request.data.get('answers', [])
        
        if not answers:
            return Response({
                'error': '답안이 제공되지 않았습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # UserQuizAttempt 생성
            quiz_attempt = UserQuizAttempt.objects.create(user=user)
            
            correct_count = 0
            total_questions = len(answers)
            results = []
            
            for answer_data in answers:
                question_id = answer_data.get('question_id')
                choice_id = answer_data.get('choice_id')
                
                try:
                    question = Question.objects.get(id=question_id)
                    choice = Choice.objects.get(id=choice_id, question=question)
                    
                    # UserAnswer 생성
                    user_answer = UserAnswer.objects.create(
                        quiz_attempt=quiz_attempt,
                        question=question,
                        selected_choice=choice,
                        is_correct=choice.is_correct
                    )
                    
                    if choice.is_correct:
                        correct_count += 1
                    
                    # 정답 찾기
                    correct_choice = question.choices.filter(is_correct=True).first()
                    
                    results.append({
                        'question_id': question.id,
                        'question_text': question.text,
                        'selected_choice': choice.text,
                        'is_correct': choice.is_correct,
                        'correct_choice': correct_choice.text if correct_choice else '',
                        'explanation': question.explanation
                    })
                    
                except (Question.DoesNotExist, Choice.DoesNotExist):
                    return Response({
                        'error': f'유효하지 않은 문제 또는 선택지입니다.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 점수 계산 및 저장
            score = (correct_count / total_questions) * 100
            quiz_attempt.score = score
            quiz_attempt.save()
            
            return Response({
                'score': score,
                'correct_count': correct_count,
                'total_questions': total_questions,
                'results': results,
                'quiz_attempt_id': quiz_attempt.id
            })
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_quiz_history(request):
    """사용자의 퀴즈 기록 조회"""
    try:
        user = request.user
        attempts = UserQuizAttempt.objects.filter(user=user).order_by('-created_at')
        serializer = UserQuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_quiz_difficulties(request):
    """퀴즈 난이도 목록 조회"""
    difficulties = [
        {'value': 'youth', 'label': '청소년'},
        {'value': 'adult_basic', 'label': '성인 기본'},
        {'value': 'adult_advanced', 'label': '성인 심화'}
    ]
    return Response(difficulties)

# 학습용 API들
@api_view(['GET'])
def question_list(request):
    """모든 문제 목록 조회 (학습용) - 선택지 순서 랜덤"""
    try:
        difficulty = request.GET.get('difficulty')
        
        if difficulty:
            questions = Question.objects.filter(difficulty=difficulty)
        else:
            questions = Question.objects.all()
        
        # 각 문제의 선택지 순서를 랜덤하게 섞기
        questions_data = []
        for question in questions:
            choices = list(question.choices.all())
            random.shuffle(choices)
            
            question_data = {
                'id': question.id,
                'text': question.text,
                'difficulty': question.difficulty,
                'explanation': question.explanation,
                'keywords': question.keywords,
                'choices': [
                    {
                        'id': choice.id,
                        'text': choice.text,
                        'is_correct': choice.is_correct
                    }
                    for choice in choices
                ]
            }
            questions_data.append(question_data)
        
        return Response(questions_data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def question_detail(request, question_id):
    """개별 문제 상세 조회 - 선택지 순서 랜덤"""
    try:
        question = get_object_or_404(Question, id=question_id)
        
        # 선택지 순서를 랜덤하게 섞기
        choices = list(question.choices.all())
        random.shuffle(choices)
        
        question_data = {
            'id': question.id,
            'text': question.text,
            'difficulty': question.difficulty,
            'explanation': question.explanation,
            'keywords': question.keywords,
            'choices': [
                {
                    'id': choice.id,
                    'text': choice.text,
                    'is_correct': choice.is_correct
                }
                for choice in choices
            ]
        }
        
        return Response(question_data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, question_id):
    """개별 문제 답안 제출 및 즉시 채점"""
    try:
        question = get_object_or_404(Question, id=question_id)
        choice_id = request.data.get('choice_id')
        
        if not choice_id:
            return Response({
                'error': '선택지가 제공되지 않았습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            selected_choice = Choice.objects.get(id=choice_id, question=question)
        except Choice.DoesNotExist:
            return Response({
                'error': '유효하지 않은 선택지입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 정답 찾기
        correct_choice = question.choices.filter(is_correct=True).first()
        
        return Response({
            'question_id': question.id,
            'question_text': question.text,
            'selected_choice': {
                'id': selected_choice.id,
                'text': selected_choice.text
            },
            'correct_choice': {
                'id': correct_choice.id,
                'text': correct_choice.text
            },
            'is_correct': selected_choice.is_correct,
            'explanation': question.explanation
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def category_list(request):
    """문제 카테고리 목록 조회"""
    try:
        categories = QuestionCategory.objects.all()
        categories_data = [
            {
                'id': category.id,
                'name': category.name,
                'description': category.description
            }
            for category in categories
        ]
        return Response(categories_data)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 새로 추가: 개념 학습용 API들
@api_view(['GET'])
def get_categories_by_difficulty(request, difficulty):
    """난이도별 카테고리 목록 조회"""
    try:
        # 해당 난이도의 문제들이 속한 카테고리만 조회
        categories = QuestionCategory.objects.filter(
            questions__difficulty=difficulty
        ).distinct()
        
        categories_data = []
        for category in categories:
            # 각 카테고리별 문제 수 계산
            question_count = Question.objects.filter(
                difficulty=difficulty, 
                category=category
            ).count()
            
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'question_count': question_count
            })
        
        return Response({
            'difficulty': difficulty,
            'categories': categories_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_concept_study_questions(request, difficulty, category_id):
    """개념 학습용 문제 조회 (해설 포함)"""
    try:
        category = get_object_or_404(QuestionCategory, id=category_id)
        
        # 해당 난이도와 카테고리의 모든 문제 조회
        questions = Question.objects.filter(
            difficulty=difficulty,
            category=category
        ).order_by('id')
        
        questions_data = []
        for question in questions:
            # 선택지는 정답이 맨 앞에 오도록 정렬 (개념 학습용)
            choices = list(question.choices.all())
            correct_choice = next((c for c in choices if c.is_correct), None)
            other_choices = [c for c in choices if not c.is_correct]
            
            # 정답을 맨 앞에, 나머지는 그대로
            ordered_choices = [correct_choice] + other_choices if correct_choice else choices
            
            question_data = {
                'id': question.id,
                'text': question.text,
                'difficulty': question.difficulty,
                'explanation': question.explanation,
                'keywords': question.keywords,
                'category': {
                    'id': category.id,
                    'name': category.name
                },
                'choices': [
                    {
                        'id': choice.id,
                        'text': choice.text,
                        'is_correct': choice.is_correct
                    }
                    for choice in ordered_choices
                ]
            }
            questions_data.append(question_data)
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description
            },
            'difficulty': difficulty,
            'questions': questions_data,
            'total_questions': len(questions_data)
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)