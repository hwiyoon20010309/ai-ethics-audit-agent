# 사용자 피드백 수집 (콘솔 기반)
# agents/human_feedback.py
def collect_feedback(assessment: dict) -> str:
    """
    콘솔에서 사람 피드백 한 줄 입력.
    고위험 항목(>=4) 나열 후 의견 수집.
    """
    high = {k:v for k,v in assessment["scores"].items() if v.get("score",3) >= 4}
    if not high:
        return ""

    print("\n=== 🤔 Human Feedback 단계 (고위험 항목) ===")
    for k, v in high.items():
        print(f"- {k}: {v.get('score')}점 / {v.get('comment')}")
    print("\n의견을 한 줄로 입력하면 해당 키워드를 RAG 재검색에 반영합니다.")
    fb = input("피드백> ").strip()
    return fb
