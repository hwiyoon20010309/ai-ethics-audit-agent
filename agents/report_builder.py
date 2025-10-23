# agents/report_builder.py
import os, json, datetime, re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase.pdfmetrics import registerFont

# ========== 🧩 폰트 설정 (나눔고딕 절대경로) ==========
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FONT_DIR = os.path.join(BASE_DIR, "fonts")
    REGULAR = os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")
    BOLD = os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")

    if not (os.path.exists(REGULAR) and os.path.exists(BOLD)):
        raise FileNotFoundError(f"❌ 폰트 없음: {FONT_DIR}")

    registerFont(ttfonts.TTFont('NanumGothic', REGULAR))
    registerFont(ttfonts.TTFont('NanumGothicBold', BOLD))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleKor', fontName='NanumGothicBold', fontSize=24,
                              alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name='HeadingKor', fontName='NanumGothicBold', fontSize=15,
                              textColor=HexColor('#1A237E'), spaceBefore=12, spaceAfter=8))
    styles.add(ParagraphStyle(name='NormalKor', fontName='NanumGothic', fontSize=10,
                              leading=14, alignment=TA_LEFT, spaceAfter=4))
    styles.add(ParagraphStyle(name='QuoteKor', fontName='NanumGothic', fontSize=10,
                              textColor=HexColor('#424242'), leftIndent=12, backColor=HexColor('#FAFAFA'),
                              borderPadding=(4, 4, 4, 4)))
    styles.add(ParagraphStyle(name='FooterKor', fontName='NanumGothic', fontSize=8,
                              alignment=TA_CENTER, textColor=HexColor('#9E9E9E')))
except Exception as e:
    print(f"⚠️ 폰트 로드 실패: {e}")
    styles = getSampleStyleSheet()


def _format_text(text):
    text = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.replace("\n", "<br/>")


# ========== 📘 헤더·푸터 ==========
def header_footer(canvas, doc):
    canvas.saveState()
    page_width = doc.width + doc.leftMargin + doc.rightMargin
    page_height = doc.height + doc.topMargin + doc.bottomMargin
    canvas.setFont('NanumGothicBold', 10)
    canvas.setFillColor(HexColor('#424242'))
    canvas.drawString(doc.leftMargin, page_height - 15 * mm, "AI 윤리 리스크 진단 보고서")
    page_num = f"Page {canvas.getPageNumber()}"
    canvas.setFont('NanumGothic', 9)
    canvas.setFillColor(HexColor('#616161'))
    canvas.drawRightString(page_width - doc.rightMargin, 15 * mm, page_num)
    canvas.restoreState()


# ========== 📄 보고서 생성 ==========
def generate_report(service_info, initial_assessment, final_assessment, recommendations, feedback=None):
    os.makedirs("outputs/reports", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    service_name = service_info.get("name", "Unknown").replace(" ", "_")
    md_path = f"outputs/reports/report_{service_name}_{ts}.md"
    pdf_path = f"outputs/reports/report_{service_name}_{ts}.pdf"

    # --- 🪶 Markdown 버전 ---
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 🤖 AI 윤리 리스크 진단 보고서\n\n")
            f.write(f"**진단 대상:** {service_info.get('name')}\n")
            f.write(f"**진단 일시:** {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n")
            f.write("---\n")
            f.write("## 📘 서비스 개요\n")
            f.write(f"- 유형: {service_info.get('type')}\n- 목적: {service_info.get('purpose')}\n\n")

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

            f.write("\n## 💡 최종 개선 권고안\n\n")
            f.write(recommendations + "\n")
        print(f"📝 Markdown 리포트 생성 완료: {md_path}")
    except Exception as e:
        print(f"🚨 Markdown 생성 오류: {e}")

    # --- 📊 PDF 버전 ---
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=inch/2, rightMargin=inch/2,
                            topMargin=25 * mm, bottomMargin=25 * mm)
    elems = [
        Paragraph("AI 윤리 리스크 진단 보고서", styles["TitleKor"]),
        Spacer(1, 6),
        Paragraph(f"<b>진단 대상:</b> {_format_text(service_info.get('name',''))}", styles["NormalKor"]),
        Paragraph(f"<b>진단 일시:</b> {datetime.datetime.now():%Y-%m-%d %H:%M}", styles["NormalKor"]),
        Spacer(1, 10),

        Paragraph("Ⅰ. 서비스 개요", styles["HeadingKor"]),
        Paragraph(f"<b>서비스 유형:</b> {_format_text(service_info.get('type',''))}", styles["NormalKor"]),
        Paragraph(f"<b>주요 목적:</b> {_format_text(service_info.get('purpose',''))}", styles["NormalKor"]),
        Spacer(1, 10),

        Paragraph("Ⅱ. 초기 윤리 리스크 평가", styles["HeadingKor"]),
    ]

    # 표 형태로 초기 평가 표시
    init_table_data = [["항목", "점수", "설명"]]
    for k, v in initial_assessment.items():
        init_table_data.append([k, str(v.get("score", "-")), v.get("comment", "")])
    init_table = Table(init_table_data, colWidths=[60*mm, 20*mm, 90*mm])
    init_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EAF6")),
        ("BOX", (0, 0), (-1, -1), 0.25, HexColor("#1A237E")),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#9FA8DA")),
        ("FONTNAME", (0, 0), (-1, 0), "NanumGothicBold"),
        ("FONTNAME", (0, 1), (-1, -1), "NanumGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elems += [init_table, Spacer(1, 8)]

    if feedback:
        elems += [
            Paragraph("Ⅲ. 사용자 피드백", styles["HeadingKor"]),
            Paragraph(_format_text(feedback), styles["QuoteKor"]),
            Spacer(1, 8),
        ]

    # 재평가 비교표
    elems += [Paragraph("Ⅳ. 피드백 반영 후 재평가 결과", styles["HeadingKor"])]
    comp_table_data = [["항목", "변경 전", "변경 후", "차이"]]
    for k, v in final_assessment.items():
        old = initial_assessment.get(k, {}).get("score", "-")
        new = v.get("score", "-")
        delta = (new - old) if isinstance(new, (int, float)) and isinstance(old, (int, float)) else "-"
        comp_table_data.append([k, str(old), str(new), str(delta)])
    comp_table = Table(comp_table_data, colWidths=[60*mm, 25*mm, 25*mm, 25*mm])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8F5E9")),
        ("BOX", (0, 0), (-1, -1), 0.25, HexColor("#388E3C")),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#A5D6A7")),
        ("FONTNAME", (0, 0), (-1, 0), "NanumGothicBold"),
        ("FONTNAME", (0, 1), (-1, -1), "NanumGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elems += [comp_table, Spacer(1, 10)]

    elems += [
        Paragraph("Ⅴ. 최종 개선 권고안", styles["HeadingKor"]),
        Paragraph(_format_text(recommendations), styles["NormalKor"]),
        Spacer(1, 10),
        Paragraph("※ 본 보고서는 Human-in-the-loop 기반 AI 윤리 평가 결과입니다.", styles["FooterKor"])
    ]

    doc.build(elems, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"📄 PDF 리포트 생성 완료: {pdf_path}")
