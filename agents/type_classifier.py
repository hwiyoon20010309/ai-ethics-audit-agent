# AI 서비스 유형 분류
# agents/type_classifier.py
import json
from langchain_openai import ChatOpenAI

def classify_service(service_description: str) -> str:
    """생성형 / 예측형 / 추천형 중 하나로 분류"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    prompt = f"""
다음 서비스 설명을 보고 유형을 한글로 정확히 한 단어로 분류하세요.
선택지는 '생성형' / '예측형' / '추천형' 중 하나입니다.
JSON으로만 답하세요. 예: {{"type":"생성형"}}

설명:
{service_description}
"""
    resp = llm.invoke(prompt)
    try:
        t = json.loads(resp.content).get("type", "").strip()
        if t in ["생성형", "예측형", "추천형"]:
            return t
    except Exception:
        pass
    return "생성형"  # 기본값
