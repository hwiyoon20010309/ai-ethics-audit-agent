# agents/rag_retriever.py
from langchain_community.vectorstores import Chroma
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

def retrieve_guidelines(query_terms: str, feedback: str = None):
    """
    RAG 검색 수행
    - feedback이 있으면 query 확장
    - feedback이 없으면 기본 검색
    """
    retriever = ensure_retriever()
    if feedback:
        query_terms = f"{query_terms} {feedback}"
        print(f"🧩 피드백 기반 RAG 재검색 수행 중... → {query_terms}")

    results = retriever.get_relevant_documents(query_terms)
    contexts = [r.page_content for r in results]
    print(f"🔍 검색된 문서 수: {len(contexts)}")
    return "\n\n".join(contexts)
