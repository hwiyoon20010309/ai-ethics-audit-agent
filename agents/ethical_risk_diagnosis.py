# 윤리 기준(EU AI Act, OECD, UNESCO)에 따른 리스크 평가 수행
# agents/ethical_risk_diagnosis.py
import os, json
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# === RAG 세팅 ===
def build_retriever():
    loader = DirectoryLoader("./data", glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(split_docs, embeddings, persist_directory="./chroma_db")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

retriever = build_retriever()

def ethical_risk_agent(state):
    """윤리 리스크 진단 (RAG 기반)"""
    ai_type = state["service_info"].get("type", "기타")
    profile = state["service_profile"]

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    query = f"""
    [{ai_type}] AI 서비스의 윤리 리스크를 10대 항목별로 평가하세요.
    근거 문서는 EU AI Act, OECD AI Principles, UNESCO Ethics.
    JSON 형식으로 출력하세요:
    {{
      "공정성": {{"score": 1~5, "comment": "..." }},
      "편향성": ...
    }}
    서비스 개요: {profile}
    """

    result = qa.run(query)

    try:
        data = json.loads(result)
    except:
        data = {"error": "JSON 변환 실패", "raw": result}

    return {"risk_assessment": data}
