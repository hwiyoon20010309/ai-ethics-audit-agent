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

def generate_recommendations(assessment: dict) -> dict:
    """
    각 항목별 리스크 수준과 실행지침 텍스트 반환
    """
    recs = {}
    for cat, info in assessment["scores"].items():
        s = int(info.get("score", 3))
        level = _level(s)

        # 간단 규칙 기반 샘플 권고안
        actions = []
        if s >= 4:
            actions = [
                "운영정책 문서화 및 대외 공개",
                "데이터 품질/편향 점검 절차 도입 및 감사 로그 저장",
                "고위험 플로우에 인간 검토 게이트 추가"
            ]
        elif s == 3:
            actions = [
                "월간 리스크 모니터링 및 샘플 검증",
                "고객 공지/FAQ에 관련 항목 추가",
            ]
        else:
            actions = ["분기별 셀프 체크 및 변화 감시"]

        recs[cat] = {
            "risk_level": level,
            "actions": actions,
            "guideline": _guideline_hint(cat)
        }
    return recs
