# 리스크 결과를 바탕으로 항목별 개선 권고안 생성
# agents/improvement_suggestion.py
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os, json

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def improvement_agent(state):
    """국제 가이드라인 기반 개선 권고안 생성 (RAG 결합)"""
    assessment = state["risk_assessment"]
    ai_type = state["service_info"].get("type", "AI")

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    query = f"""
    다음은 {ai_type} AI의 윤리 리스크 평가 결과입니다.
    국제 AI 윤리 기준(EU AI Act, OECD, UNESCO)에 따라
    각 항목별 개선 권고안을 제안하세요.

    결과:
    {json.dumps(assessment, ensure_ascii=False)}

    출력 형식:
    {{
      "Transparency": {{
        "risk_level": "High/Medium/Low",
        "recommendations": ["..."],
        "related_guideline": "EU AI Act Art.13"
      }}
    }}
    """

    response = qa.run(query)
    try:
        rec = json.loads(response)
    except:
        rec = {"error": "JSON 변환 실패", "raw": response}

    return {"recommendations": rec}
