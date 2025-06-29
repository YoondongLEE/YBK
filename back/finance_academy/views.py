from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
import os
from .models import Question, Choice, UserQuizAttempt, UserAnswer, QuestionCategory, Assessment, Certificate
from .serializers import QuestionForQuizSerializer, UserQuizAttemptSerializer, QuestionSerializer
from .certificate_generator import CertificateGenerator
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

# 새로 추가: Assessment 관련 뷰들
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_assessment(request):
    """평가 시작 - 랜덤 10문제 출제 (선택지 순서 랜덤)"""
    difficulty = request.data.get('difficulty')
    
    if not difficulty:
        return Response({'error': '난이도를 선택해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 해당 난이도의 모든 문제 가져오기
    questions = list(Question.objects.filter(difficulty=difficulty))
    
    if len(questions) < 10:
        return Response({'error': '문제가 부족합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 랜덤하게 10문제 선택
    selected_questions = random.sample(questions, 10)
    
    # 문제 데이터 직렬화 (정답 정보 제외하되, 선택지 순서 랜덤)
    questions_data = []
    for q in selected_questions:
        # 선택지들을 가져와서 랜덤하게 섞기
        choices = list(q.choices.all())
        random.shuffle(choices)
        
        choices_data = []
        for choice in choices:
            choices_data.append({
                'id': choice.id,
                'text': choice.text
                # is_correct는 클라이언트에 전송하지 않음 (평가용)
            })
        
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'choices': choices_data,
            'explanation': q.explanation
        })
    
    return Response({
        'questions': questions_data,
        'total_questions': 10
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """평가 제출 및 채점"""
    try:
        user = request.user
        difficulty = request.data.get('difficulty')
        answers = request.data.get('answers')  # {question_id: choice_id}
        
        print(f"[Debug] Assessment 제출 - 사용자: {user.username}, 난이도: {difficulty}")
        
        if not all([difficulty, answers]):
            return Response({'error': '필수 데이터가 누락되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 정답 확인 및 채점
        correct_count = 0
        question_results = []
        
        for question_id, choice_id in answers.items():
            try:
                question = Question.objects.get(id=question_id)
                selected_choice = Choice.objects.get(id=choice_id, question=question)
                correct_choice = question.choices.filter(is_correct=True).first()
                
                is_correct = selected_choice.is_correct
                if is_correct:
                    correct_count += 1
                
                question_results.append({
                    'question_id': question_id,
                    'question': question.text,
                    'user_answer': selected_choice.text,
                    'correct_answer': correct_choice.text if correct_choice else '',
                    'is_correct': is_correct,
                    'explanation': question.explanation
                })
            except (Question.DoesNotExist, Choice.DoesNotExist):
                continue
        
        # 점수 계산 (100점 만점)
        score_percentage = (correct_count / 10) * 100
        passed = score_percentage >= 60
        
        # 등급 결정
        grade = get_grade(difficulty, score_percentage)
        
        print(f"[Debug] 점수: {correct_count}/10, 등급: {grade}, 합격: {passed}")
        
        # 평가 결과 저장
        assessment = Assessment.objects.create(
            user=user,
            difficulty=difficulty,
            score=correct_count,
            total_questions=10,
            score_percentage=score_percentage,
            grade=grade,
            passed=passed,
            questions_data=question_results
        )
        
        print(f"[Debug] Assessment 저장 완료: {assessment.id}")
        
        # 합격 시 수료증 자동 생성
        certificate_info = None
        if passed:
            try:
                print(f"[Debug] 수료증 자동 생성 시작")
                generator = CertificateGenerator()
                certificate = generator.create_certificate(
                    user=user,
                    difficulty=difficulty,
                    score=correct_count,
                    total_questions=10
                )
                certificate_info = {
                    'id': certificate.id,
                    'certificate_number': certificate.certificate_number,
                    'grade': certificate.grade
                }
                print(f"[Debug] 수료증 자동 생성 완료: {certificate.id}")
            except Exception as e:
                print(f"[Debug] 수료증 자동 생성 실패: {e}")
        
        response_data = {
            'assessment_id': assessment.id,
            'score': correct_count,
            'total_questions': 10,
            'score_percentage': score_percentage,
            'grade': grade,
            'passed': passed,
            'question_results': question_results
        }
        
        if certificate_info:
            response_data['certificate'] = certificate_info
        
        return Response(response_data)
        
    except Exception as e:
        print(f"[Debug] Assessment 제출 오류: {str(e)}")
        import traceback
        print(f"[Debug] 스택 트레이스: {traceback.format_exc()}")
        return Response({'error': f'평가 제출 중 오류가 발생했습니다: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_grade(difficulty, score_percentage):
    """난이도별 등급 결정"""
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
    else:
        return 'F'  # 불합격

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assessment_history(request):
    """사용자의 평가 이력 조회"""
    try:
        assessments = Assessment.objects.filter(user=request.user).order_by('-created_at')
        
        results = []
        for assessment in assessments:
            results.append({
                'id': assessment.id,
                'difficulty': assessment.difficulty,
                'score': assessment.score,
                'total_questions': assessment.total_questions,
                'grade': assessment.grade,
                'passed': assessment.passed,
                'score_percentage': assessment.score_percentage,
                'taken_at': assessment.created_at
            })
        
        return Response(results)
        
    except Exception as e:
        print(f"[Debug] 평가 이력 조회 오류: {str(e)}")
        return Response({'error': '평가 이력을 가져올 수 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assessment_detail(request, assessment_id):
    """평가 상세 결과 조회"""
    try:
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        
        return Response({
            'id': assessment.id,
            'difficulty': assessment.difficulty,
            'score': assessment.score,
            'total_questions': assessment.total_questions,
            'grade': assessment.grade,
            'passed': assessment.passed,
            'score_percentage': assessment.score_percentage,
            'questions_data': assessment.questions_data,
            'created_at': assessment.created_at
        })
        
    except Exception as e:
        print(f"[Debug] 평가 상세 조회 오류: {str(e)}")
        return Response({'error': '평가 상세 정보를 가져올 수 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 수료증 관련 뷰들
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_certificate(request, assessment_id):
    """평가 결과를 바탕으로 수료증 생성"""
    try:
        print(f"[Debug] 수료증 생성 요청 - Assessment ID: {assessment_id}, 사용자: {request.user.username}")
        
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        
        if not assessment.passed:
            return Response({
                'error': '합격한 평가만 수료증을 발급할 수 있습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 기존 수료증 확인
        existing_cert = Certificate.objects.filter(
            user=request.user,
            difficulty=assessment.difficulty
        ).first()
        
        if existing_cert:
            print(f"[Debug] 기존 수료증 발견: {existing_cert.id}")
            return Response({
                'certificate_id': existing_cert.id,
                'certificate_number': existing_cert.certificate_number,
                'grade': existing_cert.grade,
                'file_path': existing_cert.file_path,
                'message': '기존 수료증을 반환합니다.'
            })
        
        # 새 수료증 생성
        print(f"[Debug] 새 수료증 생성 시작")
        generator = CertificateGenerator()
        certificate = generator.create_certificate(
            user=request.user,
            difficulty=assessment.difficulty,
            score=assessment.score,
            total_questions=assessment.total_questions or 10
        )
        
        return Response({
            'certificate_id': certificate.id,
            'certificate_number': certificate.certificate_number,
            'grade': certificate.grade,
            'file_path': certificate.file_path,
            'message': '수료증이 성공적으로 생성되었습니다.'
        })
        
    except Assessment.DoesNotExist:
        print(f"[Debug] Assessment를 찾을 수 없음 - ID: {assessment_id}")
        return Response({'error': 'Assessment를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"[Debug] 수료증 생성 오류: {str(e)}")
        import traceback
        print(f"[Debug] 스택 트레이스: {traceback.format_exc()}")
        return Response({'error': f'수료증 생성 중 오류가 발생했습니다: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_certificate(request, certificate_id):
    """수료증 이미지 파일 다운로드 (파일 없으면 자동 재생성)"""
    try:
        print(f"[Debug] 수료증 다운로드 요청 - 사용자: {request.user.username}, ID: {certificate_id}")
        
        certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
        file_path = os.path.join(settings.MEDIA_ROOT, certificate.file_path)
        
        print(f"[Debug] 파일 경로: {file_path}")
        print(f"[Debug] MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"[Debug] 상대 경로: {certificate.file_path}")
        print(f"[Debug] 파일 존재 여부: {os.path.exists(file_path)}")
        
        # 파일이 없거나 손상된 경우 자동 재생성
        need_regenerate = False
        
        if not os.path.exists(file_path):
            print(f"[Debug] 파일이 존재하지 않음 - 재생성 필요")
            need_regenerate = True
        else:
            # 파일 크기 확인 (0바이트면 손상된 것)
            try:
                file_size = os.path.getsize(file_path)
                print(f"[Debug] 파일 크기: {file_size} bytes")
                if file_size == 0:
                    print(f"[Debug] 파일이 비어있음 - 재생성 필요")
                    need_regenerate = True
            except Exception as size_error:
                print(f"[Debug] 파일 크기 확인 실패: {size_error} - 재생성 필요")
                need_regenerate = True
        
        # 재생성이 필요한 경우
        if need_regenerate:
            print(f"[Debug] 수료증 파일 재생성 시작")
            
            try:
                # CertificateGenerator로 재생성
                generator = CertificateGenerator()
                new_certificate = generator.create_certificate(
                    user=request.user,
                    difficulty=certificate.difficulty,
                    score=certificate.score,
                    total_questions=certificate.total_questions or 10
                )
                
                # 기존 Certificate 객체의 파일 경로 업데이트
                certificate.file_path = new_certificate.file_path
                certificate.certificate_number = new_certificate.certificate_number
                certificate.save()
                
                # 새로운 Certificate 객체 삭제 (중복 방지)
                new_certificate.delete()
                
                # 새 파일 경로로 업데이트
                file_path = os.path.join(settings.MEDIA_ROOT, certificate.file_path)
                
                print(f"[Debug] 재생성 완료: {file_path}")
                
            except Exception as regenerate_error:
                print(f"[Debug] 재생성 실패: {regenerate_error}")
                import traceback
                print(f"[Debug] 재생성 스택 트레이스: {traceback.format_exc()}")
                raise Http404("수료증 파일을 재생성할 수 없습니다.")
        
        # 파일 다운로드
        if os.path.exists(file_path):
            print(f"[Debug] 파일 다운로드 시작")
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    print(f"[Debug] 파일 읽기 성공: {len(file_data)} bytes")
                    
                    response = HttpResponse(file_data, content_type='image/png')
                    
                    # 한글 파일명을 위한 인코딩
                    filename = f"{certificate.certificate_number}_수료증.png"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    response['Content-Length'] = len(file_data)
                    
                    print(f"[Debug] 다운로드 응답 생성 완료")
                    return response
                    
            except Exception as file_error:
                print(f"[Debug] 파일 읽기 실패: {file_error}")
                raise Http404("수료증 파일을 읽을 수 없습니다.")
        else:
            print(f"[Debug] 재생성 후에도 파일이 없음")
            raise Http404("수료증 파일을 생성할 수 없습니다.")
            
    except Certificate.DoesNotExist:
        print(f"[Debug] 수료증을 찾을 수 없음 - ID: {certificate_id}")
        raise Http404("수료증을 찾을 수 없습니다.")
    except Exception as e:
        print(f"[Debug] 다운로드 오류: {str(e)}")
        import traceback
        print(f"[Debug] 스택 트레이스: {traceback.format_exc()}")
        raise Http404(f"수료증을 다운로드할 수 없습니다: {str(e)}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_certificates(request):
    """사용자의 수료증 목록 조회"""
    try:
        certificates = Certificate.objects.filter(user=request.user).order_by('-created_at')
        
        results = []
        for cert in certificates:
            results.append({
                'id': cert.id,
                'difficulty': cert.difficulty,
                'certificate_number': cert.certificate_number,
                'grade': cert.grade,
                'score': cert.score,
                'total_questions': cert.total_questions,
                'score_percentage': cert.score_percentage,
                'created_at': cert.created_at,
                'file_path': cert.file_path
            })
        
        return Response(results)
        
    except Exception as e:
        print(f"[Debug] 수료증 목록 조회 오류: {str(e)}")
        return Response({'error': '수료증 목록을 가져올 수 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)