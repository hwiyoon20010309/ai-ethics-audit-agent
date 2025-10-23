import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate_risks(state):
    """
    RAG 문맥 기반 윤리 리스크 평가
    - 입력: state (policy_context, human_feedback)
    - 출력: state["risk_assessment"]
    """
    policy_context = state.get("policy_context", "")
    feedback = state.get("human_feedback", None)

    base_prompt = (
        "다음은 AI 윤리 가이드라인 문맥입니다.\n"
        "이 내용을 바탕으로 각 항목(공정성, 편향성, 투명성, 설명가능성, 프라이버시 등)에 대해 "
        "1~5점으로 평가하고, 간단한 코멘트를 제공하세요.\n"
    )

    if feedback:
        base_prompt += f"\n사용자 피드백: {feedback}\n"
        print("💡 사용자 피드백을 반영한 재평가 수행 중...")

    # === 문맥 처리 ===
    if isinstance(policy_context, list):
        policy_text = "\n\n".join(
            [getattr(doc, "page_content", str(doc)) for doc in policy_context]
        )
    else:
        policy_text = str(policy_context)

    prompt = f"{base_prompt}\n=== 문맥 ===\n{policy_text[:4000]}"

    # === LLM 호출 ===
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    result = response.choices[0].message.content

    # ✅ 평가 결과 파싱
    state["risk_assessment"] = _parse_evaluation(result)
    print("✅ 윤리 리스크 평가 완료.")
    return state


def _parse_evaluation(result_text: str):
    """LLM 출력 결과를 dict 형태로 파싱 (Markdown, 번호, 별표, 잡음 줄 무시)"""
    assessment = {}
    lines = result_text.strip().split("\n")

    for line in lines:
        clean_line = line.strip()

        # ① "점수:" "평균:" "Summary" 등 불필요한 줄은 건너뜀
        if not clean_line or any(x in clean_line for x in ["점수:", "평균", "Summary", "총점", "평가"]):
            continue

        # ② Markdown 기호 제거 (###, ** 등)
        clean_line = re.sub(r"[*#]+", "", clean_line)
        clean_line = re.sub(r"^\s*\d+\.\s*", "", clean_line)  # "1. ", "2." 제거

        # ③ "공정성 (Fairness): 4점" 또는 "Privacy: 3/5" 등 인식
        match = re.search(
            r"([가-힣A-Za-z\s\(\)]+)\s*[:\-]?\s*(\d+(?:\.\d+)?)(?:\s*/\s*[1-5]|점)?",
            clean_line
        )
        if match:
            key = match.group(1).strip()
            score = float(match.group(2))
            assessment[key] = {"score": score, "comment": clean_line}

    # ④ 아무 항목도 잡히지 않으면 Summary로 저장
    if not assessment:
        assessment["Summary"] = {"comment": result_text}

    return assessment




