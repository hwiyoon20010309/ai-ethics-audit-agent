# 리스크 진단 + 개선안 → Markdown 및 PDF 리포트 생성
# agents/report_generation.py
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def report_agent(state):
    """리포트 자동 생성"""
    report_summary = {
        "title": f"AI 윤리 리스크 진단 결과 ({state['service_info']['type']})",
        "summary": f"{state['service_info']['type']} AI에 대한 윤리 리스크 평가 결과입니다.",
        "service": state.get("service_info", {}),
        "assessment": state.get("risk_assessment", {}),
        "recommendations": state.get("recommendations", {})
    }

    pdf_path = "outputs/ethics_audit_report.pdf"
    os.makedirs("outputs", exist_ok=True)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = [Paragraph("<b>AI Ethics Audit Report</b>", styles["Title"]), Spacer(1, 20)]

    for section, content in report_summary.items():
        elements.append(Paragraph(f"<b>{section.capitalize()}</b>", styles["Heading2"]))
        elements.append(Paragraph(json.dumps(content, ensure_ascii=False, indent=2), styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)

    return {
        "report_summary": report_summary,
        "report_final": pdf_path
    }
