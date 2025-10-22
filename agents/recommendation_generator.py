# 개선안 제안
# agents/recommendation_generator.py
def _level(score: int) -> str:
    if score >= 4: return "높음"
    if score == 3: return "중간"
    return "낮음"

def _guideline_hint(category: str) -> str:
    mapping = {
        "공정성": "OECD AI Principles (Inclusive Growth)",
        "편향성": "UNESCO (Non-discrimination), EU AI Act (Data governance)",
        "투명성": "EU AI Act Article 13, UNESCO Transparency",
        "설명가능성": "OECD Transparency & Explainability",
        "책임성": "EU AI Act (Accountability), OECD Accountability",
        "프라이버시": "EU AI Act (Data governance), OECD Privacy Framework",
        "안전성": "EU AI Act (Safety & Robustness)",
        "사회적 영향": "UNESCO (Human rights & Dignity)",
        "지속가능성": "UNESCO (Environmental & Social well-being)",
        "인간 감독": "EU AI Act Article 14 (Human oversight)"
    }
    return mapping.get(category, "OECD/UNESCO General Principle")

def generate_recommendations(risk_assessment, guideline_contexts=None):
    """
    윤리 리스크 평가 결과 및 RAG 근거 문맥을 기반으로 개선안 생성
    """
    # RAG 문맥 문자열화
    if isinstance(guideline_contexts, list):
        context_text = "\n\n".join(
            [getattr(doc, "page_content", str(doc)) for doc in guideline_contexts]
        )
    else:
        context_text = str(guideline_contexts or "")

    from openai import OpenAI
    import os
    from dotenv import load_dotenv
    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    base_prompt = (
        "다음은 AI 서비스의 윤리 리스크 평가 결과입니다.\n"
        "각 항목별로 구체적인 개선 권고안을 제시하세요.\n"
        "가능하다면 EU/OECD/UNESCO 가이드라인의 원칙과 연결하여 설명하세요.\n"
    )

    prompt = (
        f"{base_prompt}\n\n"
        f"=== 리스크 평가 ===\n{risk_assessment}\n\n"
        f"=== 참고 문맥 ===\n{context_text[:3000]}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content

