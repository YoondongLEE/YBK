import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from datetime import datetime
from .models import Certificate

class CertificateGenerator:
    def __init__(self):
        # 프로젝트 내부의 폰트 경로 설정
        self.font_dir = os.path.join(settings.BASE_DIR, 'fonts')
        
        # 폰트 경로 설정 (프로젝트 내부 폰트 사용)
        try:
            self.regular_font_path = os.path.join(self.font_dir, 'NotoSansKR-Regular.ttf')
            self.bold_font_path = os.path.join(self.font_dir, 'NotoSansKR-Bold.ttf')
            
            print(f"[Debug] 폰트 디렉토리: {self.font_dir}")
            print(f"[Debug] Regular 폰트 경로: {self.regular_font_path}")
            print(f"[Debug] Bold 폰트 경로: {self.bold_font_path}")
            print(f"[Debug] Regular 폰트 존재: {os.path.exists(self.regular_font_path)}")
            print(f"[Debug] Bold 폰트 존재: {os.path.exists(self.bold_font_path)}")
            
        except Exception as e:
            print(f"[Debug] 폰트 경로 설정 오류: {e}")
    
    def get_font(self, size, bold=False):
        """폰트 객체 반환 (한글 지원)"""
        try:
            font_path = self.bold_font_path if bold else self.regular_font_path
            
            if os.path.exists(font_path):
                print(f"[Debug] 폰트 로드 시도: {font_path}, size: {size}")
                font = ImageFont.truetype(font_path, size)
                print(f"[Debug] 폰트 로드 성공")
                return font
            else:
                print(f"[Debug] 폰트 파일이 없음: {font_path}")
                print(f"[Debug] 기본 폰트 사용")
                return ImageFont.load_default()
                
        except Exception as e:
            print(f"[Debug] 폰트 로드 실패: {e}")
            print(f"[Debug] 기본 폰트 사용")
            return ImageFont.load_default()
    
    def create_certificate(self, user, difficulty, score, total_questions=10):
        """한글 지원 수료증 생성"""
        try:
            print(f"[Debug] 수료증 생성 시작 - 사용자: {user.username}")
            
            # 캔버스 생성
            width, height = 800, 600
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # 폰트 준비
            title_font = self.get_font(36, bold=True)
            subtitle_font = self.get_font(24, bold=True)
            text_font = self.get_font(18)
            name_font = self.get_font(28, bold=True)
            
            # 등급 및 점수 계산
            score_percentage = (score / total_questions) * 100
            grade = self.get_grade(difficulty, score_percentage)
            
            # 배경 테두리
            draw.rectangle([20, 20, width-20, height-20], outline='black', width=3)
            draw.rectangle([30, 30, width-30, height-30], outline='gold', width=2)
            
            # 제목
            title_text = "Youth Banking Korea"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((width - title_width) // 2, 60), title_text, fill='black', font=title_font)
            
            # 부제목
            subtitle_text = "금융 이해력 인증서"
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            draw.text(((width - subtitle_width) // 2, 110), subtitle_text, fill='black', font=subtitle_font)
            
            # 수료증 번호
            cert_number = self.generate_certificate_number()
            number_text = f"인증서 번호: {cert_number}"
            draw.text((60, 160), number_text, fill='black', font=text_font)
            
            # 성명
            name_text = f"성명: {user.username}"
            draw.text((60, 200), name_text, fill='black', font=name_font)
            
            # 난이도
            difficulty_text = f"난이도: {self.get_difficulty_korean(difficulty)}"
            draw.text((60, 240), difficulty_text, fill='black', font=text_font)
            
            # 점수 및 등급
            score_text = f"점수: {score}/{total_questions}점 ({score_percentage:.1f}%)"
            draw.text((60, 280), score_text, fill='black', font=text_font)
            
            grade_text = f"등급: {grade}"
            draw.text((60, 320), grade_text, fill='black', font=text_font)
            
            # 발급일
            issue_date = datetime.now().strftime('%Y년 %m월 %d일')
            date_text = f"발급일: {issue_date}"
            draw.text((60, 360), date_text, fill='black', font=text_font)
            
            # 인증 문구
            cert_text = "위 사람은 금융 이해력 평가를 통과하였음을 인증합니다."
            cert_bbox = draw.textbbox((0, 0), cert_text, font=text_font)
            cert_width = cert_bbox[2] - cert_bbox[0]
            draw.text(((width - cert_width) // 2, 420), cert_text, fill='black', font=text_font)
            
            # 발급기관
            org_text = "Youth Banking Korea"
            org_bbox = draw.textbbox((0, 0), org_text, font=subtitle_font)
            org_width = org_bbox[2] - org_bbox[0]
            draw.text(((width - org_width) // 2, 480), org_text, fill='black', font=subtitle_font)
            
            # 파일 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user.username}_{difficulty}_{grade}_{timestamp}.png"
            file_path = os.path.join('certificates', filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 이미지 저장
            image.save(full_path, 'PNG')
            print(f"[Debug] 수료증 파일 저장: {full_path}")
            
            # 데이터베이스 저장
            certificate = Certificate.objects.create(
                user=user,
                difficulty=difficulty,
                certificate_number=cert_number,
                grade=grade,
                score=score,
                total_questions=total_questions,
                score_percentage=score_percentage,
                file_path=file_path
            )
            
            print(f"[Debug] 수료증 생성 완료: {certificate.id}")
            return certificate
            
        except Exception as e:
            print(f"[Debug] 수료증 생성 실패: {e}")
            import traceback
            print(f"[Debug] 스택 트레이스: {traceback.format_exc()}")
            raise
    
    def get_difficulty_korean(self, difficulty):
        """난이도 한글 변환"""
        difficulty_map = {
            'youth': '청소년',
            'adult_basic': '성인 기본',
            'adult_advanced': '성인 심화'
        }
        return difficulty_map.get(difficulty, difficulty)
    
    def get_grade(self, difficulty, score_percentage):
        """등급 결정"""
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
            return 'F'
    
    def generate_certificate_number(self):
        """수료증 번호 생성"""
        year = datetime.now().year
        count = Certificate.objects.count() + 1
        return f"{year}-{count:03d}"