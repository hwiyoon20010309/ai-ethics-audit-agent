# RAG: 윤리 가이드라인 검색 (EU, OECD, UNESCO)
# agents/rag_retriever.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

DATA_DIR = "data"
DB_DIR = os.path.join(DATA_DIR, "vectorstore")

def _load_docs():
    docs = []
    # txt
    if os.path.isdir(DATA_DIR):
        docs += DirectoryLoader(DATA_DIR, glob="*.txt", loader_cls=TextLoader, encoding="utf-8").load()
    # pdf
    for fn in os.listdir(DATA_DIR):
        if fn.lower().endswith(".pdf"):
            docs += PyMuPDFLoader(os.path.join(DATA_DIR, fn)).load()
    if not docs:
        raise FileNotFoundError("data/ 폴더에 PDF 또는 TXT가 없습니다.")
    return docs

def _build_store():
    os.makedirs(DB_DIR, exist_ok=True)
    docs = _load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    vs = Chroma.from_documents(
        chunks,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=DB_DIR
    )
    vs.persist()
    return vs

def _get_store():
    if os.path.isdir(DB_DIR) and os.listdir(DB_DIR):
        return Chroma(persist_directory=DB_DIR, embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"))
    return _build_store()

def retrieve_guidelines(queries_or_keywords) -> dict:
    """
    입력 리스트(카테고리/키워드)를 받아 Top-k 근거 문단을 반환.
    return: {query: [{"source":..., "content":...}, ...]}
    """
    vs = _get_store()
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    results = {}
    for q in queries_or_keywords:
        docs = retriever.get_relevant_documents(str(q))
        results[q] = [{"source": d.metadata.get("source","unknown"), "content": d.page_content.strip()} for d in docs]
    return results
