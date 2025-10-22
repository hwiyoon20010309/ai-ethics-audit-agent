# 윤리 리스크 평가 및 스코어 산출
# agents/risk_evaluator.py
import json
from statistics import mean
from langchain_openai import ChatOpenAI

CATEGORIES = [
    "공정성","편향성","투명성","설명가능성","책임성",
    "프라이버시","안전성","사회적 영향","지속가능성","인간 감독"
]

def evaluate_risks(service_profile: dict, guideline_context: dict) -> dict:
    """
    guideline_context: {query:[{source,content},...]}
    return:
    {
      "scores": {category: {"score": int, "comment":"...", "references":[...]}, ...},
      "total_score": float
    }
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    # 컨텍스트 문자열 생성(근거 인용 포함)
    ctx_lines = []
    for k, lst in guideline_context.items():
        for it in lst:
            ctx_lines.append(f"[{k}] ({it['source']}) {it['content'][:600]}")
    ctx = "\n\n".join(ctx_lines[:12])  # 과다 컨텍스트 방지

    prompt = f"""
[국제 가이드라인 근거 문단]
{ctx}

[서비스 개요]
{json.dumps(service_profile, ensure_ascii=False)}

위 근거를 기준으로, 아래 10개 윤리 항목에 대해
1(낮은 리스크)~5(높은 리스크)로 평가하고 코멘트를 작성하세요.
JSON만 출력:
{{
  "scores": {{
    "공정성": {{"score": 1-5, "comment": "...", "references": ["문서/조항 요약 1", "..."]}},
    "편향성": {{...}},
    ...
  }}
}}
"""
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        scores = data.get("scores", {})
    except Exception:
        # 최소 fallback
        scores = {c: {"score": 3, "comment": "기준 부족으로 기본 점수", "references": []} for c in CATEGORIES}

    # total_score는 보수적으로 "최댓값" 또는 "평균" 중 택1. 여기선 최댓값.
    total = max([v.get("score", 3) for v in scores.values()] + [3])
    return {"scores": scores, "total_score": total}
