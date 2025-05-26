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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_pjt.settings')
    django.setup()
    
    print("🚀 프로젝트 초기 설정을 시작합니다...\n")
    
    try:
        # 1. 마이그레이션
        print("1️⃣ 데이터베이스 마이그레이션 중...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 마이그레이션 완료\n")
        
        # 2. 금속 가격 데이터 로드
        print("2️⃣ 금속 가격 데이터 로드 중...")
        execute_from_command_line([
            'manage.py', 'loaddata', 
            'finance_info/fixtures/gold_prices.json',
            'finance_info/fixtures/silver_prices.json'
        ])
        execute_from_command_line(['manage.py', 'load_metal_prices'])
        print("✅ 금속 가격 데이터 로드 완료\n")
        
        # 3. 더미 사용자 데이터 로드
        print("3️⃣ 더미 사용자 데이터 로드 중...")
        try:
            execute_from_command_line([
                'manage.py', 'loaddata',
                'accounts/fixtures/dummy_users.json',
                'accounts/fixtures/dummy_deposit_subscriptions.json',
                'accounts/fixtures/dummy_saving_subscriptions.json'
            ])
            print("✅ 더미 사용자 데이터 로드 완료\n")
        except Exception as e:
            print(f"⚠️ 더미 데이터 로드 실패: {e}")
            print("💡 더미 데이터가 없다면 다음 명령어로 생성하세요:")
            print("   python manage.py create_and_save_dummy_data\n")
        
        print("🎉 프로젝트 초기 설정이 완료되었습니다!")
        print("🔥 개발 서버를 시작하려면: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ 설정 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()