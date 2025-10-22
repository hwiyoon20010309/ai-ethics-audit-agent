# agents/service_crawler.py
import os
import requests
from bs4 import BeautifulSoup
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def crawl_service_info(service_name: str, max_results: int = 3) -> str:
    """
    AI 서비스 이름을 입력받아 Tavily API로 검색 후, 웹페이지를 크롤링하고 요약 반환
    """
    print(f"🌐 '{service_name}' 관련 웹 정보 수집 중...")

    # 1️⃣ Tavily API로 검색 (langchain community tool)
    search = TavilySearchResults(max_results=max_results)
    results = search.run(f"{service_name} AI 서비스 설명 OR 기술 구조 OR product overview")

    if not results:
        print("⚠️ 검색 결과가 없습니다.")
        return ""

    # 2️⃣ 각 페이지에서 본문 추출
    texts = []
    for r in results:
        try:
            url = r["url"]
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            paragraphs = " ".join([p.get_text() for p in soup.find_all("p")])
            texts.append(paragraphs)
            print(f"   📄 {url} 수집 완료")
        except Exception as e:
            print(f"   ⚠️ {r['url']} 수집 실패: {e}")
            continue

    if not texts:
        return ""

    combined_text = " ".join(texts)[:15000]  # 너무 긴 텍스트는 잘라냄

    # 3️⃣ LLM 요약
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    prompt = f"""
    다음은 '{service_name}'에 대한 웹에서 수집한 설명입니다.
    기술적 구조, 서비스 목적, 주요 기능 중심으로 간결하게 요약해줘.
    -----
    {combined_text}
    """
    summary = llm.invoke(prompt)
    print("✅ 요약 완료")
    return summary.content
