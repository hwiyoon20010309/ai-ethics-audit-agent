# agents/risk_evaluator.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def evaluate_risks(policy_context: str, feedback: str = None):
    """
    RAG 문맥 기반 윤리 리스크 평가
    - feedback이 있으면 평가 prompt에 반영하여 재평가
    """
    base_prompt = (
        "다음은 AI 윤리 가이드라인 문맥입니다.\n"
        "이 내용을 바탕으로 각 항목(공정성, 편향성, 투명성, 설명가능성, 프라이버시 등)에 대해 "
        "1~5점으로 평가하고, 간단한 코멘트를 제공하세요.\n"
    )

    if feedback:
        base_prompt += f"\n사용자 피드백: {feedback}\n"
        print("💡 사용자 피드백을 반영한 재평가 수행 중...")

    prompt = f"{base_prompt}\n=== 문맥 ===\n{policy_context[:4000]}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    result = response.choices[0].message.content
    return parse_evaluation(result)

def parse_evaluation(result_text: str):
    """
    단순 텍스트 파서: LLM 출력 → dict 변환
    """
    import re
    assessment = {}
    lines = result_text.strip().split("\n")
    for line in lines:
        match = re.match(r"(\w+)\s*[:\-]\s*(\d(?:\.\d)?)", line)
        if match:
            key = match.group(1).strip()
            score = float(match.group(2))
            assessment[key] = {"score": score, "comment": line}
    if not assessment:
        assessment["Summary"] = {"score": 0, "comment": result_text}
    return assessment
