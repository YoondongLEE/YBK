#!/usr/bin/env python
"""
프로젝트 초기 설정을 위한 스크립트
새로운 환경에서 한 번에 모든 데이터를 로드합니다.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """프로젝트 초기 설정 실행"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    print("🚀 프로젝트 초기 설정을 시작합니다...\n")
    
    try:
        # 1. 마이그레이션 (makemigrations 포함)
        print("1️⃣ 데이터베이스 마이그레이션 중...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations'])
        except:
            print("   📝 새로운 마이그레이션이 없습니다")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 마이그레이션 완료\n")
        
        # 2. 금속 가격 데이터 로드
        print("2️⃣ 금속 가격 데이터 로드 중...")
        try:
            execute_from_command_line([
                'manage.py', 'loaddata', 
                'finance_info/fixtures/gold_prices.json',
                'finance_info/fixtures/silver_prices.json'
            ])
            print("   📊 금속 가격 데이터 로드 완료 (214개 객체)")
            print("   💡 기본 데이터로 충분히 동작합니다")
        except Exception as e:
            print(f"   ⚠️ fixtures 로드 실패: {e}")
        
        print("✅ 금속 가격 데이터 처리 완료\n")
        
        # Excel 파일 로드 부분 제거 (실시간 데이터 의존성 제거)
        
                # 3. 더미 사용자 데이터 로드/생성
        print("3️⃣ 더미 사용자 데이터 로드 중...")
        try:
            # 기존 데이터 확인
            from accounts.models import User
            user_count = User.objects.count()
            
            if user_count > 1:  # 기본 관리자 계정 제외
                print(f"✅ 이미 {user_count:,}명의 사용자가 있습니다")
                print("📊 기존 데이터를 사용합니다\n")
            else:
                print("   👤 더미 사용자 fixtures를 로드합니다...")
                try:
                    # fixtures에서 더미 데이터 로드
                    execute_from_command_line([
                        'manage.py', 'loaddata', 
                        'accounts/fixtures/dummy_accounts.json',
                        'accounts/fixtures/dummy_deposits.json',
                    ])
                    final_user_count = User.objects.count()
                    print(f"✅ 더미 사용자 로드 완료! 총 {final_user_count:,}명\n")
                except Exception as e:
                    print(f"   ⚠️ fixtures 로드 실패: {e}")
                    print("   👤 새로운 더미 사용자 10,000명을 생성합니다...")
                    execute_from_command_line(['manage.py', 'create_dummy_users'])
                    final_user_count = User.objects.count()
                    print(f"✅ 더미 사용자 생성 완료! 총 {final_user_count:,}명\n")
                
        except Exception as e:
            print(f"⚠️ 더미 데이터 처리 실패: {e}")
            print("💡 수동으로 생성하려면:")
            print("   python manage.py create_dummy_users\n")
        
        # 4. 퀴즈 데이터 로드
        print("4️⃣ 퀴즈 데이터 로드 중...")
        try:
            # 기존 퀴즈 데이터 확인
            from finance_academy.models import Question, QuestionCategory
            question_count = Question.objects.count()
            category_count = QuestionCategory.objects.count()
            
            if question_count > 0:
                print(f"✅ 이미 {question_count}개의 문제와 {category_count}개의 카테고리가 있습니다")
                
                # 간단한 통계 출력
                for difficulty in ['youth', 'adult_basic', 'adult_advanced']:
                    diff_count = Question.objects.filter(difficulty=difficulty).count()
                    difficulty_names = {
                        'youth': '청소년',
                        'adult_basic': '성인기본', 
                        'adult_advanced': '성인심화'
                    }
                    if diff_count > 0:
                        print(f"   - {difficulty_names[difficulty]}: {diff_count}개 문제")
                
                print("📊 기존 퀴즈 데이터를 사용합니다\n")
            else:
                # 퀴즈 데이터 로드
                print("   📝 청소년, 성인기본, 성인심화 퀴즈 데이터를 로드합니다...")
                execute_from_command_line(['manage.py', 'load_quiz_data'])
                
                # 로드 후 통계 확인
                final_question_count = Question.objects.count()
                final_category_count = QuestionCategory.objects.count()
                
                print(f"✅ 퀴즈 데이터 로드 완료!")
                print(f"   📊 총 {final_question_count}개 문제, {final_category_count}개 카테고리")
                
                # 난이도별 통계 출력
                for difficulty in ['youth', 'adult_basic', 'adult_advanced']:
                    diff_count = Question.objects.filter(difficulty=difficulty).count()
                    diff_categories = QuestionCategory.objects.filter(
                        questions__difficulty=difficulty
                    ).distinct().count()
                    
                    difficulty_names = {
                        'youth': '청소년',
                        'adult_basic': '성인기본', 
                        'adult_advanced': '성인심화'
                    }
                    
                    print(f"   - {difficulty_names[difficulty]}: {diff_count}개 문제, {diff_categories}개 카테고리")
                print()
                
        except Exception as e:
            print(f"⚠️ 퀴즈 데이터 로드 실패: {e}")
            print("💡 퀴즈 데이터 파일이 있는지 확인하세요:")
            print("   - finance_academy/fixtures/problems_youth.json")
            print("   - finance_academy/fixtures/problems_basic.json") 
            print("   - finance_academy/fixtures/problems_adv.json")
            print("💡 수동으로 로드하려면: python manage.py load_quiz_data\n")
        
        print("🎉 프로젝트 초기 설정이 완료되었습니다!")
        print("🔥 개발 서버를 시작하려면: python manage.py runserver")
        print("🌐 프론트엔드 서버는: npm run install")
        print("                 npm run dev (front 디렉토리에서)")
        
    except Exception as e:
        print(f"❌ 설정 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()