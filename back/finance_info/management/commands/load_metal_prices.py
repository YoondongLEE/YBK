import os
import pandas as pd
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from finance_info.models import MetalPrice
from datetime import datetime
from django.conf import settings

class Command(BaseCommand):
    help = 'Load metal prices from Excel files and create fixtures'

    def handle(self, *args, **kwargs):
        # 파일 경로 설정 - final-pjt/data 폴더 직접 지정
        data_dir = Path('/Users/iyundong/Desktop/SSAFY/1학기_관통/final-pjt-v1/final-pjt/data')
        
        # 디버깅을 위한 경로 출력
        self.stdout.write(f'Looking for data in: {data_dir}')
        
        gold_file = data_dir / 'Gold_prices.xlsx'
        silver_file = data_dir / 'Silver_prices.xlsx'
        
        # 파일 존재 확인
        if not gold_file.exists():
            self.stdout.write(self.style.ERROR(f'Gold data file not found at: {gold_file}'))
            return
            
        if not silver_file.exists():
            self.stdout.write(self.style.ERROR(f'Silver data file not found at: {silver_file}'))
            return
        
        # 기존 데이터 삭제
        MetalPrice.objects.all().delete()
        
        # 금 가격 데이터 로드 - 날짜 형식과 가격 컬럼을 명확하게 지정
        self.load_data(gold_file, 'gold', date_format='custom', price_column='Close/Last')
        
        # 은 가격 데이터 로드 - 날짜 형식과 가격 컬럼을 명확하게 지정
        self.load_data(silver_file, 'silver', date_format='custom', price_column='Close/Last')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded metal price data'))
        
        # 데이터를 fixtures로 저장
        self.create_fixtures()
    
    def load_data(self, file_path, metal_type, date_format='custom', price_column='Close/Last'):
        try:
            # Excel 파일 읽기
            df = pd.read_excel(file_path)
            
            # 데이터 확인을 위한 로깅 추가
            self.stdout.write(f"Excel 파일 내용 미리보기: {metal_type}")
            self.stdout.write(str(df.head(3)))
            self.stdout.write(f"컬럼명: {df.columns.tolist()}")
            
            # 날짜 컬럼은 항상 'Date'
            date_col = 'Date'
            
            # 가격 컬럼은 매개변수로 받음
            price_col = price_column
            
            # 컬럼명 확인
            if date_col not in df.columns:
                self.stdout.write(self.style.ERROR(f"'{date_col}' 컬럼이 없습니다. 컬럼명: {df.columns.tolist()}"))
                return
            
            if price_col not in df.columns:
                self.stdout.write(self.style.ERROR(f"'{price_col}' 컬럼이 없습니다. 컬럼명: {df.columns.tolist()}"))
                return
            
            # 데이터 변환 및 저장
            bulk_data = []
            failed_count = 0
            
            for idx, row in df.iterrows():
                try:
                    date_str = row[date_col]
                    price = row[price_col]

                    # 날짜 처리 (기존 코드 유지)
                    if isinstance(date_str, pd.Timestamp):
                        date_obj = date_str.date()
                    elif isinstance(date_str, datetime):
                        date_obj = date_str.date()
                    elif isinstance(date_str, str):
                        date_parts = date_str.split('.')
                        if len(date_parts) == 3:
                            year = int(date_parts[0])
                            month = int(date_parts[1])
                            day = int(date_parts[2])
                            date_obj = datetime(year, month, day).date()
                        else:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        continue

                    # 가격 처리: 쉼표 제거 후 float 변환
                    if isinstance(price, str):
                        price = price.replace(',', '')
                        try:
                            price = float(price)
                        except ValueError:
                            self.stdout.write(f"가격 변환 오류 (행 {idx+1}): {row[price_col]}")
                            continue

                    if pd.isna(price) or not isinstance(price, (int, float)) or price <= 0:
                        continue

                    metal_price = MetalPrice(
                        metal_type=metal_type,
                        date=date_obj,
                        price=price
                    )
                    bulk_data.append(metal_price)
                except Exception as e:
                    self.stdout.write(f"행 {idx+1} 처리 중 오류: {str(e)}")
                    failed_count += 1
            
            # 데이터 일괄 저장
            if bulk_data:
                MetalPrice.objects.bulk_create(bulk_data)
                self.stdout.write(self.style.SUCCESS(f'Loaded {len(bulk_data)} {metal_type} prices'))
                self.stdout.write(f'Failed to load {failed_count} rows for {metal_type}')
            else:
                self.stdout.write(self.style.WARNING(f'No valid data found for {metal_type}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading {metal_type} data: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def create_fixtures(self):
        try:
            # fixtures 디렉토리 생성
            fixtures_dir = os.path.join(settings.BASE_DIR, 'finance_info', 'fixtures')
            os.makedirs(fixtures_dir, exist_ok=True)
            
            # 기존 fixtures 파일 삭제
            for fixture_file in ['gold_prices.json', 'silver_prices.json']:
                fixture_path = os.path.join(fixtures_dir, fixture_file)
                if os.path.exists(fixture_path):
                    os.remove(fixture_path)
                    self.stdout.write(f'Removed existing fixture file: {fixture_path}')
            
            # 금 데이터 counts 확인
            gold_count = MetalPrice.objects.filter(metal_type='gold').count()
            silver_count = MetalPrice.objects.filter(metal_type='silver').count()
            
            self.stdout.write(f'금 데이터 레코드 수: {gold_count}')
            self.stdout.write(f'은 데이터 레코드 수: {silver_count}')
            
            # 금 데이터만 필터링하여 저장
            gold_data = []
            for item in MetalPrice.objects.filter(metal_type='gold'):
                gold_data.append({
                    'model': 'finance_info.metalprice',
                    'pk': item.id,
                    'fields': {
                        'metal_type': item.metal_type,
                        'date': item.date.strftime('%Y-%m-%d'),
                        'price': item.price
                    }
                })
                
            if gold_data:
                gold_fixture_path = os.path.join(fixtures_dir, 'gold_prices.json')
                with open(gold_fixture_path, 'w') as f:
                    json.dump(gold_data, f, indent=4)
                self.stdout.write(self.style.SUCCESS(f'Created gold fixtures at {gold_fixture_path} with {len(gold_data)} records'))
            else:
                self.stdout.write(self.style.WARNING('No gold data to save in fixtures'))
            
            # 은 데이터만 필터링하여 저장
            silver_data = []
            for item in MetalPrice.objects.filter(metal_type='silver'):
                silver_data.append({
                    'model': 'finance_info.metalprice',
                    'pk': item.id,
                    'fields': {
                        'metal_type': item.metal_type,
                        'date': item.date.strftime('%Y-%m-%d'),
                        'price': item.price
                    }
                })
                
            if silver_data:
                silver_fixture_path = os.path.join(fixtures_dir, 'silver_prices.json')
                with open(silver_fixture_path, 'w') as f:
                    json.dump(silver_data, f, indent=4)
                self.stdout.write(self.style.SUCCESS(f'Created silver fixtures at {silver_fixture_path} with {len(silver_data)} records'))
            else:
                self.stdout.write(self.style.WARNING('No silver data to save in fixtures'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating fixtures: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())