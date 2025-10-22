# AI 서비스 유형 분류
# agents/type_classifier.py
import json
from langchain_openai import ChatOpenAI

def classify_service(purpose: str) -> dict:
    """AI 서비스 목적을 기반으로 유형 분류"""
    purpose = purpose.lower()

    if any(word in purpose for word in ["생성", "작성", "요약", "이미지", "번역"]):
        service_type = "생성형 AI"
    elif any(word in purpose for word in ["추천", "큐레이션", "랭킹", "검색"]):
        service_type = "추천형 AI"
    elif any(word in purpose for word in ["예측", "분류", "진단", "탐지"]):
        service_type = "예측형 AI"
    else:
        service_type = "기타"

    return {"type": service_type}
