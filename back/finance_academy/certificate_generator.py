import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Certificate
import urllib.request

User = get_user_model()

def load_font(size):
    """
    한글 폰트를 로드합니다. 없으면 온라인에서 다운로드합니다.
    """
    # 폰트 저장 디렉토리
    font_dir = os.path.join(settings.BASE_DIR, 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    # 로컬 폰트 경로들 (우선순위 순)
    local_font_paths = [
        # 다운로드된 폰트
        os.path.join(font_dir, 'NanumGothic.ttf'),
        os.path.join(font_dir, 'malgun.ttf'),
        
        # 시스템 폰트들
        "/System/Library/Fonts/AppleGothic.ttf",  # macOS
        "/Windows/Fonts/malgun.ttf",  # Windows
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux (nanum)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux fallback
        
        # 상대 경로들
        "malgun.ttf",
        "AppleGothic.ttf",
        "NanumGothic.ttf",
    ]
    
    # 로컬 폰트 먼저 시도
    for font_path in local_font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except (IOError, OSError) as e:
            print(f"폰트 로드 실패: {font_path} - {e}")
            continue
    
    # 나눔고딕 폰트 다운로드 시도
    nanum_font_path = os.path.join(font_dir, 'NanumGothic.ttf')
    if not os.path.exists(nanum_font_path):
        try:
            print("나눔고딕 폰트 다운로드 중...")
            nanum_url = "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothic.ttf"
            urllib.request.urlretrieve(nanum_url, nanum_font_path)
            print(f"나눔고딕 폰트 다운로드 완료: {nanum_font_path}")
            return ImageFont.truetype(nanum_font_path, size)
        except Exception as e:
            print(f"나눔고딕 폰트 다운로드 실패: {e}")
    
    # 구글 폰트 다운로드 시도
    noto_font_path = os.path.join(font_dir, 'NotoSansKR.ttf')
    if not os.path.exists(noto_font_path):
        try:
            print("Noto Sans KR 폰트 다운로드 중...")
            noto_url = "https://fonts.gstatic.com/s/notosanskr/v36/PbykFmXiEBPT4ITbgNA5Cgm20xz64px-1LxgLeqmvuQM.ttf"
            urllib.request.urlretrieve(noto_url, noto_font_path)
            print(f"Noto Sans KR 폰트 다운로드 완료: {noto_font_path}")
            return ImageFont.truetype(noto_font_path, size)
        except Exception as e:
            print(f"Noto Sans KR 폰트 다운로드 실패: {e}")
    
    print("모든 한글 폰트 로드 실패, 기본 폰트 사용")
    return ImageFont.load_default()


class CertificateGenerator:
    def __init__(self):
        self.template_path = os.path.join(
            settings.BASE_DIR, 'assets', 'YBK_certificate_form_withoutdate.png'
        )
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
        os.makedirs(self.output_dir, exist_ok=True)

        # 한글 과정명 매핑
        self.difficulty_kr = {
            'youth': '청소년',
            'adult_basic': '성인 기본',
            'adult_advanced': '성인 심화',
        }

        # 등급 영문 풀 네임 매핑
        self.grade_full_name = {
            'AH': 'Advanced High',
            'AM': 'Advanced Mid',
            'AL': 'Advanced Low',
            'IH': 'Intermediate High',
            'IM': 'Intermediate Mid',
            'IL': 'Intermediate Low',
            'NH': 'Novice High',
            'NM': 'Novice Mid',
            'NL': 'Novice Low',
        }

    def create_certificate(self, user, difficulty, score, total_questions):
        """
        DB에서 등급을 계산하고, 새로 발급할지 판단한 뒤
        _generate_certificate_image를 호출하여 이미지를 만들고
        DB에 저장하거나 업데이트합니다.
        """
        percentage = (score / total_questions) * 100
        grade = Certificate.calculate_grade(difficulty, percentage)
        if not grade:
            raise ValueError("60점 미만은 수료증을 발급할 수 없습니다.")

        # 기존 수료증이 있고, 더 높은 등급이 이미 있으면 발급 안 함
        existing = Certificate.objects.filter(user=user, difficulty=difficulty).first()
        if existing:
            priority = {
                'AH': 9, 'AM': 8, 'AL': 7,
                'IH': 6, 'IM': 5, 'IL': 4,
                'NH': 3, 'NM': 2, 'NL': 1,
            }
            if priority.get(existing.grade, 0) >= priority.get(grade, 0):
                return existing

        cert_number = Certificate.generate_certificate_number()
        image_path = self._generate_certificate_image(
            user, difficulty, grade, cert_number, percentage
        )

        certificate, created = Certificate.objects.update_or_create(
            user=user,
            difficulty=difficulty,
            defaults={
                'certificate_number': cert_number,
                'grade': grade,
                'score': score,
                'total_questions': total_questions,
                'file_path': image_path,
            }
        )
        return certificate

    def _generate_certificate_image(self, user, difficulty, grade, cert_number, percentage):
        """
        실제 수료증 템플릿에 텍스트를 입히고
        파일로 저장한 후 상대경로를 반환합니다.
        """
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"수료증 템플릿을 찾을 수 없습니다: {self.template_path}")
        
        img = Image.open(self.template_path)
        draw = ImageDraw.Draw(img)
        W, H = img.size
        print(f"[Debug] Template size: {W}×{H}")

        # 폰트 설정 (한글 지원 폰트 사용)
        font_num    = load_font(15)  # 발급번호
        font_name   = load_font(18)  # 성명
        font_course = load_font(18)  # 학습 과정
        font_grade  = load_font(18)  # 이수 등급

        text_color = (70, 70, 90)

        # 텍스트 준비
        cert_txt   = cert_number
        user_name  = user.get_full_name() or user.username
        course_txt = f"{self.difficulty_kr.get(difficulty, '')} 과정"
        grade_txt  = f"{grade} ({self.grade_full_name.get(grade, '')})"

        # 한글 텍스트 테스트
        print(f"[Debug] 사용자명: {user_name}")
        print(f"[Debug] 과정명: {course_txt}")
        print(f"[Debug] 등급: {grade_txt}")

        # 1) 발급번호 (x=74.9%, y=7.3%)
        x_cert = W * 0.749 - draw.textlength(cert_txt, font=font_num)
        y_cert = H * 0.073
        draw.text((x_cert, y_cert), cert_txt, font=font_num, fill=text_color)

        # 2) 성명 (x=35%, y=39.5%)
        x_name = W * 0.35
        y_name = H * 0.395
        draw.text((x_name, y_name), user_name, font=font_name, fill=text_color)

        # 3) 학습 과정 (x=35%, y=42.5%)
        x_course = W * 0.35
        y_course = H * 0.425
        draw.text((x_course, y_course), course_txt, font=font_course, fill=text_color)

        # 4) 이수 등급 (x=35%, y=45.5%)
        x_grade = W * 0.35
        y_grade = H * 0.455
        draw.text((x_grade, y_grade), grade_txt, font=font_grade, fill=text_color)

        # 저장
        filename = f"{user.username}_{difficulty}_{grade}_{datetime.now():%Y%m%d_%H%M%S}.png"
        output_path = os.path.join(self.output_dir, filename)
        img.save(output_path, 'PNG')
        
        print(f"[Debug] 수료증 생성 완료: {output_path}")
        return f"certificates/{filename}"