# AI 서비스 설명을 분석하는 agent1
# agents/service_analysis.py
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

def service_analysis_agent(state):
    """서비스 개요 및 주요 기능 분석"""
    desc = state["service_info"]["description"]

    prompt = f"""
    다음 AI 서비스를 분석하세요:
    서비스 설명: {desc}

    아래 항목을 요약하세요:
    - 서비스 목적
    - 주요 입력/출력 데이터
    - 사용자 대상
    - 사용 기술 또는 모델 유형 (예: 생성형, 예측형 등)
    """

    response = llm.invoke(prompt)
    return {
        "service_profile": response.content,
        "service_info": state["service_info"]
    }
