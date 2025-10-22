# 서비스 기능 및 데이터 분석
# agents/service_analyzer.py
from langchain_openai import ChatOpenAI

def analyze_service(service_description: str, service_type: str) -> dict:
    """서비스 목적/입력-출력/데이터/잠재 리스크 후보 등 구조화"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = f"""
당신은 AI 감사 컨설턴트입니다.
아래 서비스 설명을 바탕으로 구조화 분석을 해주세요.

출력은 JSON:
{{
  "type": "...",
  "purpose": "...",
  "inputs": ["..."],
  "outputs": ["..."],
  "data_sources": ["..."],
  "users": ["..."],
  "sensitive_data": true/false,
  "notes": "3-5줄 요약"
}}

서비스 유형: {service_type}
설명:
{service_description}
"""
    res = llm.invoke(prompt)
    # 실패 대비: 최소 필드 보장
    base = {
        "type": service_type, "purpose": "", "inputs": [], "outputs": [],
        "data_sources": [], "users": [], "sensitive_data": False, "notes": ""
    }
    try:
        import json
        parsed = json.loads(res.content)
        base.update(parsed)
    except Exception:
        base["notes"] = res.content.strip()[:800]
    return base
