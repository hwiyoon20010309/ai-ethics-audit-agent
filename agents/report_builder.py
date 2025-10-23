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

# --- [수정됨] 폰트 설정 (나눔고딕) ---
# 프로젝트 내 report_builder.py 파일 기준으로 절대경로 설정
try:
    # 현재 파일(report_builder.py)의 실제 디렉터리 경로
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FONT_DIR = os.path.join(BASE_DIR, "fonts")

    REGULAR_FONT_PATH = os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")
    BOLD_FONT_PATH = os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")

    # print(f"[DEBUG] 폰트 경로 확인: {REGULAR_FONT_PATH}")  # ← 디버깅용, 나중에 지워도 됨

    if os.path.exists(REGULAR_FONT_PATH) and os.path.exists(BOLD_FONT_PATH):
        registerFont(ttfonts.TTFont('NanumGothic', REGULAR_FONT_PATH))
        registerFont(ttfonts.TTFont('NanumGothicBold', BOLD_FONT_PATH))

        # 기본 스타일시트 로드
        styles = getSampleStyleSheet()

        # [개선] 스타일 세분화
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
            textColor=HexColor('#1A237E')
        ))
        styles.add(ParagraphStyle(
            name='NormalKor',
            parent=styles['Normal'],
            fontName='NanumGothic',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='CodeKor',
            parent=styles['Code'],
            fontName='NanumGothic',
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            backColor=HexColor('#F5F5F5'),
            borderPadding=(5, 5, 5, 5),
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
        name='QuoteKor',
        parent=styles['Normal'],
        fontName='NanumGothicItalic' if 'NanumGothicItalic' in styles else 'NanumGothic',
        fontSize=10,
        leading=14,
        leftIndent=12,
        rightIndent=12,
        textColor=HexColor('#424242'),
        backColor=HexColor('#FAFAFA'),
        borderPadding=(4, 4, 4, 4),
        spaceBefore=6,
        spaceAfter=6,
        italic=True
        ))

        styles.add(ParagraphStyle(
            name='FooterKor',
            parent=styles['Normal'],
            fontName='NanumGothic',
            fontSize=8,
            alignment=TA_CENTER,
            textColor=HexColor('#9E9E9E'),
            spaceBefore=12,
        ))

    else:
        raise FileNotFoundError(f"❌ NanumGothic 폰트를 찾을 수 없습니다. ({REGULAR_FONT_PATH})")

except Exception as e:
    print(f"⚠️ 폰트 로드 실패: {e}")
    print("→ 'fonts/NanumGothic-Regular.ttf'와 'fonts/NanumGothic-Bold.ttf' 파일이 필요합니다.")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Heading1Kor', parent=styles['Title']))
    styles.add(ParagraphStyle(name='MetaInfo', parent=styles['Normal']))
    styles.add(ParagraphStyle(name='Heading1Kor', parent=styles['h1']))
    styles.add(ParagraphStyle(name='NormalKor', parent=styles['Normal']))
    styles.add(ParagraphStyle(name='CodeKor', parent=styles['Code']))


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


def generate_report(service_info: dict,
                    initial_assessment: dict,
                    final_assessment: dict,
                    recommendations: str,
                    feedback: str = None):
    """
    개선된 보고서 생성기
    - initial_assessment: 최초 평가 결과
    - final_assessment: 피드백 반영 후 재평가 결과
    - feedback: 사용자가 입력한 피드백 내용
    """
    os.makedirs("outputs/reports", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    service_name = service_info.get("name", "UnknownService").replace(" ", "_")
    md_path = f"outputs/reports/report_{service_name}_{ts}.md"
    pdf_path = f"outputs/reports/report_{service_name}_{ts}.pdf"

    # Markdown 버전 생성
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 🤖 AI 윤리 리스크 진단 보고서\n\n")
            f.write(f"**진단 대상:** {service_info.get('name')}\n")
            f.write(f"**진단 일시:** {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n")
            f.write("---\n")
            f.write("## 📘 서비스 개요\n")
            f.write(f"- 유형: {service_info.get('type')}\n")
            f.write(f"- 목적: {service_info.get('purpose')}\n\n")

            f.write("## 📊 초기 윤리 리스크 평가\n")
            f.write("| 항목 | 점수 | 설명 |\n|------|------|------|\n")
            for k, v in initial_assessment.items():
                f.write(f"| {k} | {v.get('score','-')} | {v.get('comment','')} |\n")
            f.write("\n")

            if feedback:
                f.write("## 💬 사용자 피드백\n")
                f.write(f"> {feedback}\n\n")

            f.write("## 🔁 피드백 반영 후 재평가 결과\n")
            f.write("| 항목 | 변경 전 | 변경 후 | 차이 |\n|------|------|------|------|\n")
            for k, v in final_assessment.items():
                old = initial_assessment.get(k, {}).get("score", "-")
                new = v.get("score", "-")
                delta = (new - old) if isinstance(new, (int, float)) and isinstance(old, (int, float)) else "-"
                f.write(f"| {k} | {old} | {new} | {delta:+} |\n")
            f.write("\n")

            f.write("## 💡 최종 개선 권고안\n\n")
            f.write(recommendations + "\n")
        print(f"📝 Markdown 리포트 생성 완료: {md_path}")
    except Exception as e:
        print(f"🚨 Markdown 생성 중 오류: {e}")

    # PDF 버전
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=inch/2, rightMargin=inch/2,
                            topMargin=25*mm, bottomMargin=25*mm)

    elems = [
        Paragraph("AI 윤리 리스크 진단 보고서", styles["TitleKor"]),
        Spacer(1, 6),
        Paragraph(f"<b>진단 대상:</b> {service_info.get('name','N/A')}", styles["MetaInfo"]),
        Paragraph(f"<b>진단 일시:</b> {datetime.datetime.now():%Y-%m-%d %H:%M}", styles["MetaInfo"]),
        Spacer(1, 10),

        Paragraph("Ⅰ. 서비스 개요", styles["Heading1Kor"]),
        Paragraph(f"<b>서비스 유형:</b> {service_info.get('type','N/A')}", styles["NormalKor"]),
        Paragraph(f"<b>주요 목적:</b> {_format_text_for_pdf(service_info.get('purpose',''))}", styles["NormalKor"]),
        Spacer(1, 8),

        Paragraph("Ⅱ. 초기 윤리 리스크 평가", styles["Heading1Kor"]),
        Preformatted(_pp(initial_assessment), styles["CodeKor"]),
    ]

    if feedback:
        elems += [
            Paragraph("Ⅲ. 사용자 피드백", styles["Heading1Kor"]),
            Paragraph(_format_text_for_pdf(feedback), styles["QuoteKor"]),
        ]

    elems += [
        Paragraph("Ⅳ. 피드백 반영 후 재평가 결과", styles["Heading1Kor"]),
        Preformatted(_pp(final_assessment), styles["CodeKor"]),
        Spacer(1, 8),

        Paragraph("Ⅴ. 최종 개선 권고안", styles["Heading1Kor"]),
        Paragraph(_format_text_for_pdf(recommendations), styles["NormalKor"]),
        Spacer(1, 10),

        Paragraph("※ 본 보고서는 Human-in-the-loop 기반 AI 윤리 평가 결과입니다.", styles["FooterKor"])
    ]

    doc.build(elems, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"📄 PDF 리포트 생성 완료: {pdf_path}")
 

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