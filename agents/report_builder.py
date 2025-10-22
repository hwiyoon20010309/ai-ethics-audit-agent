# 결과 리포트 생성 (MD/PDF)
# agents/report_builder.py
import os, json, datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def _pp(d):  # pretty print
    return json.dumps(d, ensure_ascii=False, indent=2)

def build_report(service_desc: str, service_type: str, assessment: dict, recommendations: dict):
    os.makedirs("outputs/reports", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    md_path = f"outputs/reports/ethics_report_{ts}.md"
    pdf_path = f"outputs/reports/ethics_report_{ts}.pdf"

    # Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# AI 윤리 리스크 진단 보고서\n\n")
        f.write(f"**생성일**: {datetime.datetime.now()}\n\n")
        f.write(f"## 서비스 개요\n- 유형: {service_type}\n- 설명: {service_desc}\n\n")
        f.write("## 평가 결과 (최종)\n")
        f.write("```json\n" + _pp(assessment["scores"]) + "\n```\n\n")
        f.write("## 개선 권고안\n")
        tbl = "| 항목 | 리스크 수준 | 권고안(요약) | 가이드라인 |\n|---|---|---|---|\n"
        for k, v in recommendations.items():
            actions_short = "; ".join(v["actions"][:2])
            tbl += f"| {k} | {v['risk_level']} | {actions_short} | {v['guideline']} |\n"
        f.write(tbl + "\n")
    print(f"📝 Markdown 리포트: {md_path}")

    # 간단 PDF
    try:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elems = [
            Paragraph("AI Ethics Audit Report", styles["Title"]),
            Spacer(1, 8),
            Paragraph(f"Generated at: {datetime.datetime.now()}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("<b>Service</b>", styles["Heading2"]),
            Paragraph(f"Type: {service_type}<br/>Desc: {service_desc}", styles["Normal"]),
            Spacer(1, 10),
            Paragraph("<b>Assessment (Final)</b>", styles["Heading2"]),
            Paragraph(_pp(assessment["scores"]).replace("\n","<br/>"), styles["Code"]),
            Spacer(1, 10),
            Paragraph("<b>Recommendations</b>", styles["Heading2"]),
            Paragraph(_pp(recommendations).replace("\n","<br/>"), styles["Code"]),
        ]
        doc.build(elems)
        print(f"📄 PDF 리포트: {pdf_path}")
    except Exception as e:
        print(f"⚠️ PDF 생성 실패: {e}")
