import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

VECTOR_DIR = os.path.join("data", "vectorstore")

def ensure_retriever():
    """Chroma retriever 초기화"""
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    retriever = Chroma(
        persist_directory=VECTOR_DIR,
        embedding_function=embedding
    ).as_retriever(search_kwargs={"k": 5})
    return retriever


def retrieve_guidelines(state):
    """state 기반 윤리 가이드라인 검색"""
    retriever = ensure_retriever()
    results = []
    query_terms = state.get("risk_factors", [])
    feedback = state.get("human_feedback", None)

    print("\n📚 윤리 가이드라인 근거 검색 중...")

    if isinstance(query_terms, list):
        for term in query_terms:
            query = f"{term} {feedback}" if feedback else term
            print(f"🔍 [RAG 검색] {query}")
            docs = retriever.get_relevant_documents(query)
            for d in docs[:2]:
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

    # ✅ 검색 결과를 state에 저장
    state["policy_context"] = "\n\n".join([r["content"] for r in results])
    return state
