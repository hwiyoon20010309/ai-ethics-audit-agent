# agents/rag_retriever.py
from langchain_chroma import Chroma  # ✅ 최신 버전 import
from langchain_openai import OpenAIEmbeddings
import os

VECTOR_DIR = os.path.join("data", "vectorstore")

def ensure_retriever():
    """Chroma retriever 초기화"""
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    retriever = Chroma(
        persist_directory=VECTOR_DIR,
        embedding_function=embedding
    ).as_retriever(search_kwargs={"k": 5})
    return retriever


def retrieve_guidelines(query_terms, feedback: str = None):
    """
    RAG 검색 수행
    - query_terms가 str이면 단일 검색
    - list면 각 리스크 항목별 검색
    - feedback이 있으면 query 확장
    """
    retriever = ensure_retriever()
    results = []

    # ✅ 리스트 / 문자열 모두 처리
    if isinstance(query_terms, list):
        for term in query_terms:
            query = f"{term} {feedback}" if feedback else term
            print(f"🔍 [RAG 검색] {query}")
            docs = retriever.get_relevant_documents(query)
            for d in docs[:2]:  # 상위 2개 문서만 사용
                results.append({
                    "risk": term,
                    "content": d.page_content.strip()
                })
    else:
        query = f"{query_terms} {feedback}" if feedback else query_terms
        print(f"🔍 [RAG 검색] {query}")
        docs = retriever.get_relevant_documents(query)
        for d in docs[:3]:
            results.append({
                "risk": query_terms,
                "content": d.page_content.strip()
            })

    print(f"✅ 총 검색된 문서 수: {len(results)}")
    return "\n\n".join([r["content"] for r in results])
