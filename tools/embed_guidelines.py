# tools/embed_guidelines.py
import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# === ① 환경 변수 로드 ===
load_dotenv()

DATA_DIR = "data"
VECTOR_DIR = os.path.join(DATA_DIR, "vectorstore")

def embed_guideline_pdfs():
    """EU / OECD / UNESCO 윤리 가이드라인 PDF를 벡터화하여 Chroma DB로 저장"""
    os.makedirs(VECTOR_DIR, exist_ok=True)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("🚨 OpenAI API Key가 없습니다.")
        print("👉 .env 파일에 다음 내용을 추가하세요:")
        print("OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)

    pdf_files = [
        os.path.join(DATA_DIR, "EU_AI_Act.pdf"),
        os.path.join(DATA_DIR, "OECD_AI_Principles.pdf"),
        os.path.join(DATA_DIR, "UNESCO_AI_Ethics.pdf"),
    ]

    print("📚 윤리 가이드라인 PDF 로딩 중...")
    docs = []
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            print(f"   📄 {os.path.basename(pdf_path)} 로딩 중...")
            loader = PyPDFLoader(pdf_path)
            docs.extend(loader.load())
        else:
            print(f"⚠️ {pdf_path} 파일을 찾을 수 없습니다. (건너뜀)")

    if not docs:
        print("🚫 로드된 문서가 없습니다. PDF 경로를 확인하세요.")
        sys.exit(1)

    print(f"✅ 총 {len(docs)}개 문서 로드 완료.")

    # === ② Chunking ===
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    print(f"🧩 총 {len(chunks)}개 텍스트 청크로 분할됨.")

    # === ③ Embedding + VectorDB 저장 ===
    print("🔢 임베딩 생성 및 Chroma DB 저장 중...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 최신 버전에서는 persist_directory를 지정하면 자동으로 저장됨
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DIR
    )

    print(f"✅ Chroma DB 저장 완료: {VECTOR_DIR}")

if __name__ == "__main__":
    embed_guideline_pdfs()
