# agents/report_builder.py
import os, json, datetime
from reportlab.lib.pagesizes import A4
# [수정] Preformatted (코드 블록용), colors (색상용) 임포트
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase.pdfmetrics import registerFont
import re

# --- [수정] 폰트 설정 (나눔고딕) ---
# 프로젝트 내 'fonts' 폴더에서 폰트를 로드합니다.
try:
    FONT_DIR = "fonts" 
    REGULAR_FONT_PATH = os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")
    BOLD_FONT_PATH = os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")

    if os.path.exists(REGULAR_FONT_PATH) and os.path.exists(BOLD_FONT_PATH):
        registerFont(ttfonts.TTFont('NanumGothic', REGULAR_FONT_PATH))
        registerFont(ttfonts.TTFont('NanumGothicBold', BOLD_FONT_PATH))
        
        # 기본 스타일시트 로드
        styles = getSampleStyleSheet()
        
        # [수정] 더 세분화된 스타일 정의
        styles.add(ParagraphStyle(
            name='TitleKor', 
            parent=styles['Title'], 
            fontName='NanumGothicBold',
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=18
        ))
        styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=styles['Normal'],
            fontName='NanumGothic',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='Heading1Kor', 
            parent=styles['h1'], 
            fontName='NanumGothicBold',
            fontSize=16,
            spaceBefore=12,
            spaceAfter=8,
            textColor=HexColor('#1A237E') # 진한 파란색
        ))
        styles.add(ParagraphStyle(
            name='NormalKor', 
            parent=styles['Normal'], 
            fontName='NanumGothic',
            fontSize=10,
            leading=14, # 줄 간격
            alignment=TA_LEFT, 
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='CodeKor', 
            parent=styles['Code'], 
            fontName='NanumGothic', # 코드도 나눔고딕 사용 (고정폭 폰트가 있다면 더 좋음)
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            backColor=HexColor('#F5F5F5'), # 연한 회색 배경
            borderPadding=(5, 5, 5, 5),
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=10
        ))
    else:
        raise FileNotFoundError("NanumGothic 폰트 파일을 'fonts' 폴더에서 찾을 수 없습니다.")

except Exception as e:
    print(f"⚠️ 폰트 로드 실패: {e}. PDF 한글이 깨질 수 있습니다.")
    print("-> 'fonts/NanumGothic-Regular.ttf'와 'fonts/NanumGothic-Bold.ttf' 파일이 필요합니다.")
    styles = getSampleStyleSheet()
    # 영문 스타일 별칭 (Fallback)
    styles.add(ParagraphStyle(name='TitleKor', parent=styles['Title']))
    styles.add(ParagraphStyle(name='MetaInfo', parent=styles['Normal']))
    styles.add(ParagraphStyle(name='Heading1Kor', parent=styles['h1']))
    styles.add(ParagraphStyle(name='NormalKor', parent=styles['Normal']))
    styles.add(ParagraphStyle(name='CodeKor', parent=styles['Code']))


def _pp(d):  # pretty print
    """딕셔너리나 리스트를 JSON 문자열로 예쁘게 변환"""
    try:
        return json.dumps(d, ensure_ascii=False, indent=2)
    except TypeError:
        return str(d)

def _format_text_for_pdf(text: str) -> str:
    """PDF Paragraph에 맞게 문자열 변환 (줄바꿈, HTML 태그 이스케이프)"""
    if not isinstance(text, str):
        text = str(text)
    # 1. HTML 특수 문자 이스케이프
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 2. Markdown 스타일 -> HTML 변환 (간단하게)
    text = re.sub(r"^\s*#\s(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE) # H1 -> Bold
    text = re.sub(r"^\s*##\s(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE) # H2 -> Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text) # Bold
    text = re.sub(r"^\s*[\-\*]\s(.+)$", r"• \1", text, flags=re.MULTILINE) # Bullet
    # 3. 줄바꿈을 <br/> 태그로
    text = text.replace("\n", "<br/>")
    return text

# --- [신규] PDF 헤더/푸터 그리는 함수 ---
def header_footer(canvas, doc):
    """PDF 페이지의 헤더와 푸터를 그립니다."""
    canvas.saveState()
    page_width = doc.width + doc.leftMargin + doc.rightMargin
    page_height = doc.height + doc.topMargin + doc.bottomMargin
    
    # 헤더 (보고서 제목)
    canvas.setFont('NanumGothicBold', 10)
    canvas.setFillColor(HexColor('#424242'))
    canvas.drawString(doc.leftMargin, page_height - 15 * mm, "AI 윤리 리스크 진단 보고서")
    
    # 푸터 (페이지 번호)
    page_num_text = f"Page {canvas.getPageNumber()}"
    canvas.setFont('NanumGothic', 9)
    canvas.setFillColor(HexColor('#616161'))
    canvas.drawRightString(page_width - doc.rightMargin, 15 * mm, page_num_text)
    
    canvas.restoreState()


def generate_report(service_info: dict, risk_assessment: dict, recommendations: str):
    """
    [수정됨] main.py에서 전달하는 3개의 인수를 받도록 수정
    1. service_info (dict): 서비스 정보
    2. risk_assessment (dict): 평가 결과
    3. recommendations (str): 권고안 (LLM이 생성한 문자열)
    """
    os.makedirs("outputs/reports", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    service_name = service_info.get("name", "UnknownService").replace(" ", "_")
    
    md_path = f"outputs/reports/report_{service_name}_{ts}.md"
    pdf_path = f"outputs/reports/report_{service_name}_{ts}.pdf"

    # --- 데이터 추출 ---
    service_name_display = service_info.get("name", "N/A")
    service_type = service_info.get("type", "N/A")
    service_purpose = service_info.get("purpose", "N/A")
    report_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # --- 1. Markdown 리포트 생성 (기존과 동일) ---
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# AI 윤리 리스크 진단 보고서\n\n")
            f.write(f"**진단 대상**: {service_name_display}\n")
            f.write(f"**진단 일시**: {report_date}\n\n")
            
            f.write("## 1. 서비스 개요\n\n")
            f.write(f"- **서비스 유형**: {service_type}\n")
            f.write(f"- **주요 목적**: {service_purpose}\n\n")
            
            f.write("## 2. 윤리 리스크 평가 (최종)\n\n")
            f.write("```json\n" + _pp(risk_assessment) + "\n```\n\n")
            
            f.write("## 3. 종합 개선 권고안\n\n")
            f.write(str(recommendations))
            f.write("\n")
            
        print(f"📝 Markdown 리포트 생성 완료: {md_path}")

    except Exception as e:
        print(f"🚨 Markdown 리포트 생성 중 오류 발생: {e}")

    # --- 2. PDF 리포트 생성 [수정] ---
    try:
        # [수정] 헤더/푸터 공간 확보를 위해 topMargin, bottomMargin 증가
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                rightMargin=inch/2, leftMargin=inch/2,
                                topMargin=25 * mm, bottomMargin=25 * mm) # A4 높이 297mm
        
        elems = [
            Paragraph(f"AI 윤리 리스크 진단 보고서", styles["TitleKor"]),
            Spacer(1, 6),
            Paragraph(f"<b>진단 대상:</b> {_format_text_for_pdf(service_name_display)}", styles["MetaInfo"]),
            Paragraph(f"<b>진단 일시:</b> {report_date}", styles["MetaInfo"]),
            Spacer(1, 12),
            
            Paragraph("1. 서비스 개요", styles["Heading1Kor"]),
            Paragraph(f"<b>서비스 유형:</b> {_format_text_for_pdf(service_type)}", styles["NormalKor"]),
            Paragraph(f"<b>주요 목적:</b> {_format_text_for_pdf(service_purpose)}", styles["NormalKor"]),
            Spacer(1, 10),
            
            Paragraph("2. 윤리 리스크 평가 (최종)", styles["Heading1Kor"]),
            # [수정] JSON을 Preformatted와 CodeKor 스타일로 표시
            Preformatted(_pp(risk_assessment), styles["CodeKor"]),
            Spacer(1, 10),
            
            Paragraph("3. 종합 개선 권고안", styles["Heading1Kor"]),
            Paragraph(_format_text_for_pdf(recommendations), styles["NormalKor"]),
        ]
        
        # [수정] build 시 헤더/푸터 함수 적용
        doc.build(elems, onFirstPage=header_footer, onLaterPages=header_footer)
        print(f"📄 PDF 리포트 생성 완료: {pdf_path}")
        
    except Exception as e:
        print(f"🚨 PDF 리포트 생성 중 오류 발생: {e}")