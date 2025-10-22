# 잠재적 윤리 리스크 요인 추출
# agents/risk_factor_extractor.py
from langchain_openai import ChatOpenAI

DEFAULT_CATEGORIES = [
    "공정성","편향성","투명성","설명가능성","책임성",
    "프라이버시","안전성","사회적 영향","지속가능성","인간 감독"
]

def extract_risk_factors(service_profile: dict) -> list:
    """서비스 개요 기반 잠재 리스크 키워드와 평가 카테고리 목록 생성"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = f"""
서비스 개요를 보고 잠재 윤리 리스크 키워드를 5~8개로 제시하세요.
JSON으로만: {{"keywords": ["..."]}}

서비스 개요:
{service_profile}
"""
    res = llm.invoke(prompt)
    try:
        import json
        kws = json.loads(res.content).get("keywords", [])
        if isinstance(kws, list) and kws:
            return list(dict.fromkeys(kws))  # 중복 제거
    except Exception:
        pass
    return ["데이터 편향", "투명성 부족", "설명불가", "프라이버시 위험"]
