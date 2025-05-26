from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core import serializers
from accounts.models import User
from deposits.models import DepositSubscription, SavingSubscription
import os
import json

class Command(BaseCommand):
    help = '더미 데이터를 생성하고 fixture로 저장합니다'

    def handle(self, *args, **options):
        # 1. 더미 데이터 생성
        self.stdout.write('1. 더미 사용자 데이터 생성 중...')
        call_command('create_dummy_users')
        
        # 2. fixtures 디렉토리 생성
        fixtures_dir = os.path.join('accounts', 'fixtures')
        os.makedirs(fixtures_dir, exist_ok=True)
        
        # 3. 더미 사용자 데이터 저장
        self.stdout.write('2. 더미 사용자 데이터 저장 중...')
        dummy_users = User.objects.filter(username__startswith='dummy_user_')
        
        # 사용자 데이터 저장
        users_data = serializers.serialize('json', dummy_users, indent=2)
        with open(os.path.join(fixtures_dir, 'dummy_users.json'), 'w', encoding='utf-8') as f:
            f.write(users_data)
        
        # 4. 가입 정보 저장
        self.stdout.write('3. 가입 정보 저장 중...')
        
        # 더미 사용자들의 예금 가입 정보
        dummy_user_ids = list(dummy_users.values_list('id', flat=True))
        deposit_subs = DepositSubscription.objects.filter(user_id__in=dummy_user_ids)
        saving_subs = SavingSubscription.objects.filter(user_id__in=dummy_user_ids)
        
        # 예금 가입 정보 저장
        deposit_data = serializers.serialize('json', deposit_subs, indent=2)
        with open(os.path.join(fixtures_dir, 'dummy_deposit_subscriptions.json'), 'w', encoding='utf-8') as f:
            f.write(deposit_data)
        
        # 적금 가입 정보 저장
        saving_data = serializers.serialize('json', saving_subs, indent=2)
        with open(os.path.join(fixtures_dir, 'dummy_saving_subscriptions.json'), 'w', encoding='utf-8') as f:
            f.write(saving_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ 더미 데이터 생성 및 저장 완료!\n'
                f'   - 사용자: {dummy_users.count()}명\n'
                f'   - 예금 가입: {deposit_subs.count()}건\n'
                f'   - 적금 가입: {saving_subs.count()}건\n\n'
                f'📁 저장 위치:\n'
                f'   - accounts/fixtures/dummy_users.json\n'
                f'   - accounts/fixtures/dummy_deposit_subscriptions.json\n'
                f'   - accounts/fixtures/dummy_saving_subscriptions.json'
            )
        )