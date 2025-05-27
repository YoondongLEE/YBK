import json
import os
from django.core.management.base import BaseCommand
from finance_academy.models import Question, Choice, QuestionCategory

class Command(BaseCommand):
    help = 'Load quiz data from JSON fixtures'

    def handle(self, *args, **options):
        # fixtures 폴더 경로
        fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fixtures')
        
        # 기존 데이터 삭제
        self.stdout.write('기존 퀴즈 데이터를 삭제합니다...')
        Choice.objects.all().delete()
        Question.objects.all().delete()
        QuestionCategory.objects.all().delete()
        
        # 카테고리 저장용 딕셔너리
        categories_cache = {}
        
        # 각 난이도별 JSON 파일 처리
        difficulty_files = {
            'youth': 'problems_youth.json',
            'adult_basic': 'problems_basic.json', 
            'adult_advanced': 'problems_adv.json'
        }
        
        total_questions = 0
        total_categories = 0
        
        for difficulty, filename in difficulty_files.items():
            file_path = os.path.join(fixtures_dir, filename)
            
            if not os.path.exists(file_path):
                self.stdout.write(f'파일을 찾을 수 없습니다: {file_path}')
                continue
                
            self.stdout.write(f'{difficulty} 데이터를 로드합니다...')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. 카테고리 먼저 생성
            categories_data = data.get('categories', [])
            difficulty_questions = data.get(difficulty, [])
            
            # 카테고리별 문제 ID 매핑 생성
            question_category_mapping = {}
            for category_info in categories_data:
                category_name = category_info['name']
                question_ids = category_info['questions']
                
                # 카테고리 생성 또는 가져오기
                if category_name not in categories_cache:
                    category, created = QuestionCategory.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'description': self.get_category_description(category_name)
                        }
                    )
                    categories_cache[category_name] = category
                    if created:
                        total_categories += 1
                        self.stdout.write(f'카테고리 생성: {category_name}')
                
                # 문제 ID와 카테고리 매핑
                for q_id in question_ids:
                    question_category_mapping[q_id] = categories_cache[category_name]
            
            # 2. 문제 생성
            for q_data in difficulty_questions:
                question_id = q_data['id']
                
                # 카테고리 할당 (매핑에서 찾거나 기본 카테고리)
                category = question_category_mapping.get(
                    question_id, 
                    self.get_default_category(difficulty, categories_cache)
                )
                
                # 문제 생성
                question = Question.objects.create(
                    difficulty=difficulty,
                    text=q_data['text'],
                    keywords=q_data.get('keywords', []),
                    explanation=q_data.get('explanation', ''),
                    category=category
                )
                
                # 선택지 생성
                for choice_data in q_data['choices']:
                    Choice.objects.create(
                        question=question,
                        text=choice_data['text'],
                        is_correct=choice_data['is_correct']
                    )
                
                total_questions += 1
                self.stdout.write(f'문제 생성: [{category.name}] {question.text[:50]}...')
        
        # 통계 출력
        total_choices = Choice.objects.count()
        total_db_categories = QuestionCategory.objects.count()
        
        self.stdout.write('\n=== 로드 완료 통계 ===')
        self.stdout.write(f'총 카테고리: {total_db_categories}개')
        self.stdout.write(f'총 문제: {total_questions}개')
        self.stdout.write(f'총 선택지: {total_choices}개')
        
        # 각 난이도별 카테고리 및 문제 통계
        for difficulty in ['youth', 'adult_basic', 'adult_advanced']:
            categories = QuestionCategory.objects.filter(questions__difficulty=difficulty).distinct()
            difficulty_question_count = Question.objects.filter(difficulty=difficulty).count()
            
            self.stdout.write(f'\n[{difficulty}] 총 {difficulty_question_count}개 문제, {categories.count()}개 카테고리:')
            for cat in categories:
                count = Question.objects.filter(difficulty=difficulty, category=cat).count()
                self.stdout.write(f'  - {cat.name}: {count}개 문제')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ 데이터 로드 완료!\n'
                f'카테고리: {total_db_categories}개\n'
                f'문제: {total_questions}개\n'
                f'선택지: {total_choices}개'
            )
        )

    def get_category_description(self, category_name):
        """카테고리별 설명 반환"""
        descriptions = {
            '예산·소비 관리': '가계부 작성, 지출 관리, 소비 패턴 분석 등 예산 관리 기초',
            '신용·대출 관리': '신용카드, 대출, 신용점수 관리 등 신용 관련 지식',
            '투자 기초': '주식, 펀드, ETF 등 기초 투자 상품과 투자 전략',
            '보험·리스크 관리': '각종 보험 상품과 위험 관리 방법',
            '디지털 금융 활용': '모바일 뱅킹, 핀테크 서비스 등 디지털 금융 활용법',
            '청소년 금융': '청소년을 위한 기초 금융 개념과 용돈 관리',
            '성인 기본 금융': '성인을 위한 기본적인 금융 지식과 재테크',
            '성인 심화 금융': '고급 투자, 세금, 부동산 등 심화 금융 지식'
        }
        return descriptions.get(category_name, f'{category_name} 관련 금융 지식')

    def get_default_category(self, difficulty, categories_cache):
        """난이도별 기본 카테고리 반환"""
        default_category_names = {
            'youth': '청소년 금융',
            'adult_basic': '성인 기본 금융',
            'adult_advanced': '성인 심화 금융'
        }
        
        default_name = default_category_names.get(difficulty, '기타')
        
        # 기본 카테고리가 없으면 생성
        if default_name not in categories_cache:
            category, created = QuestionCategory.objects.get_or_create(
                name=default_name,
                defaults={
                    'description': self.get_category_description(default_name)
                }
            )
            categories_cache[default_name] = category
            if created:
                self.stdout.write(f'기본 카테고리 생성: {default_name}')
        
        return categories_cache[default_name]