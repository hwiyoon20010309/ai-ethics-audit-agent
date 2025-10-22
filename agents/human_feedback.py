# agents/human_feedback.py
from typing import Dict

def collect_feedback(risk_assessment: Dict) -> str:
    """
    사용자 피드백 입력 단계
    - 점수가 높은 항목(>=4) 위주로 보여주고 의견을 입력받음
    - 입력받은 텍스트는 RAG 재검색 시 query 확장에 사용됨
    """
    print("\n⚠️ 일부 항목의 윤리 리스크 점수가 높게 평가되었습니다.")
    print("다음 항목은 우선적으로 검토가 필요합니다:\n")

    for key, value in risk_assessment.items():
        score = value.get("score", 0)
        comment = value.get("comment", "")
        if score >= 4:
            print(f" - [{key}] 점수: {score} → {comment}")

    print("\n💬 개선 또는 보완이 필요하다고 생각되는 부분을 간단히 입력하세요.")
    feedback = input("입력: ").strip()

    if not feedback:
        feedback = "No additional feedback provided."

    print(f"\n🧩 피드백 수집 완료 → '{feedback}'\n")
    return feedback
