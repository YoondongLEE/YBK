import random
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from accounts.models import User
from deposits.models import DepositProduct, SavingProduct, DepositSubscription, SavingSubscription

class Command(BaseCommand):
    help = '1,000명의 더미 사용자 데이터를 생성합니다'

    def handle(self, *args, **options):
        # 기존 더미 사용자 삭제 (실제 사용자 제외)
        dummy_users = User.objects.filter(username__startswith='dummy_user_')
        deleted_count = dummy_users.count()
        dummy_users.delete()
        self.stdout.write(f'기존 더미 사용자 {deleted_count}명 삭제')

        # 상품 목록 가져오기
        deposit_products = list(DepositProduct.objects.all())
        saving_products = list(SavingProduct.objects.all())
        
        if not deposit_products and not saving_products:
            self.stdout.write(self.style.ERROR('먼저 금융상품 데이터를 로드해주세요.'))
            return

        # 은행 코드 목록
        bank_codes = ['0010001', '0010002', '0010020', '0010030', '0010927', '0010418', '0013175']
        
        # 성향 선택지
        savings_tendencies = ['conservative', 'moderate', 'aggressive']
        investment_tendencies = ['very_conservative', 'conservative', 'moderate', 'aggressive', 'very_aggressive']

        users_created = 0
        batch_size = 100  # 배치 크기를 100으로 줄임

        for batch in range(10):  # 10 배치로 1,000명 생성
            users_to_create = []
            subscriptions_to_create = []

            for i in range(batch_size):
                user_num = batch * batch_size + i + 1
                
                # 연령대별 분포 (20대-50대 중심)
                age_ranges = [
                    (20, 29, 0.25),  # 25%
                    (30, 39, 0.35),  # 35%
                    (40, 49, 0.25),  # 25%
                    (50, 65, 0.15),  # 15%
                ]
                
                age_range = random.choices(age_ranges, weights=[r[2] for r in age_ranges])[0]
                age = random.randint(age_range[0], age_range[1])
                
                # 나이에 따른 자산 분포 (현실적인 분포)
                if age < 30:
                    assets = random.randint(100, 5000) * 10000  # 100만-5천만
                elif age < 40:
                    assets = random.randint(500, 15000) * 10000  # 500만-1.5억
                elif age < 50:
                    assets = random.randint(1000, 30000) * 10000  # 1천만-3억
                else:
                    assets = random.randint(2000, 50000) * 10000  # 2천만-5억
                
                # 나이에 따른 연봉 분포
                if age < 30:
                    annual_income = random.randint(2500, 5000) * 10000  # 2500만-5천만
                elif age < 40:
                    annual_income = random.randint(3500, 8000) * 10000  # 3500만-8천만
                elif age < 50:
                    annual_income = random.randint(4000, 12000) * 10000  # 4천만-1.2억
                else:
                    annual_income = random.randint(3000, 10000) * 10000  # 3천만-1억 (은퇴 고려)

                # 나이에 따른 성향 분포
                if age < 35:
                    savings_tendency = random.choices(savings_tendencies, weights=[0.2, 0.5, 0.3])[0]
                    investment_tendency = random.choices(investment_tendencies, weights=[0.1, 0.2, 0.4, 0.2, 0.1])[0]
                elif age < 50:
                    savings_tendency = random.choices(savings_tendencies, weights=[0.3, 0.5, 0.2])[0]
                    investment_tendency = random.choices(investment_tendencies, weights=[0.2, 0.3, 0.3, 0.15, 0.05])[0]
                else:
                    savings_tendency = random.choices(savings_tendencies, weights=[0.5, 0.4, 0.1])[0]
                    investment_tendency = random.choices(investment_tendencies, weights=[0.4, 0.4, 0.15, 0.04, 0.01])[0]

                user = User(
                    username=f'dummy_user_{user_num:04d}',  # 4자리로 변경
                    email=f'dummy{user_num}@example.com',
                    password=make_password('dummy123'),
                    age=age,
                    assets=assets,
                    annual_income=annual_income,
                    savings_tendency=savings_tendency,
                    investment_tendency=investment_tendency,
                    preferred_bank=random.choice(bank_codes),
                    is_active=True
                )
                users_to_create.append(user)

            # 사용자 일괄 생성
            created_users = User.objects.bulk_create(users_to_create)
            users_created += len(created_users)

            # 각 사용자마다 랜덤하게 상품 가입 (1-4개)
            for user in created_users:
                # 예금 상품 가입 (0-2개)
                if deposit_products:
                    deposit_count = min(random.randint(0, 2), len(deposit_products))
                    if deposit_count > 0:
                        selected_deposits = random.sample(deposit_products, deposit_count)
                        for product in selected_deposits:
                            subscriptions_to_create.append(
                                DepositSubscription(user=user, product=product)
                            )
                
                # 적금 상품 가입 (0-2개)
                if saving_products:
                    saving_count = min(random.randint(0, 2), len(saving_products))
                    if saving_count > 0:
                        selected_savings = random.sample(saving_products, saving_count)
                        for product in selected_savings:
                            subscriptions_to_create.append(
                                SavingSubscription(user=user, product=product)
                            )

            # 가입 정보 일괄 생성
            if subscriptions_to_create:
                # 예금 가입 정보 분리
                deposit_subs = [sub for sub in subscriptions_to_create if isinstance(sub, DepositSubscription)]
                saving_subs = [sub for sub in subscriptions_to_create if isinstance(sub, SavingSubscription)]
                
                if deposit_subs:
                    DepositSubscription.objects.bulk_create(deposit_subs, ignore_conflicts=True)
                if saving_subs:
                    SavingSubscription.objects.bulk_create(saving_subs, ignore_conflicts=True)

            self.stdout.write(f'배치 {batch + 1}/10 완료: {len(created_users)}명 생성')

        self.stdout.write(
            self.style.SUCCESS(f'총 {users_created}명의 더미 사용자가 생성되었습니다.')
        )