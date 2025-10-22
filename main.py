# main.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agents.type_classifier import classify_service
from agents.service_analyzer import analyze_service
from agents.risk_factor_extractor import extract_risks
from agents.rag_retriever import retrieve_guidelines
from agents.risk_evaluator import evaluate_risks
from agents.human_feedback import collect_feedback
from agents.recommendation_generator import generate_recommendations
from agents.report_builder import build_report

def main():
    print("=== 🧭 AI 윤리 리스크 진단 (RAG + Human-in-the-loop) ===")
    desc = input("진단할 AI 서비스 설명을 입력하세요:\n> ").strip()

    # 1) 유형 분류
    svc_type = classify_service(desc)
    print(f"→ 유형 분류: {svc_type}")

    # 2) 서비스 분석
    profile = analyze_service(desc, svc_type)
    print("→ 서비스 분석 완료")

    # 3) 리스크 요인 추출
    risks = extract_risks(profile)
    # 10대 카테고리도 함께 질의에 포함
    categories = ["공정성","편향성","투명성","설명가능성","책임성","프라이버시","안전성","사회적 영향","지속가능성","인간 감독"]
    queries = list(set(risks + categories))
    print(f"→ RAG 질의 키워드: {queries[:6]} ...")

    # 4) 가이드라인 검색 (RAG)
    ctx = retrieve_guidelines(queries)
    print("→ 가이드라인 검색 완료")

    # 5) 리스크 평가
    assessment = evaluate_risks(profile, ctx)
    print(f"→ 1차 평가 완료 (최고점수: {assessment['total_score']})")

    # 6) Human Feedback 루프 (고위험 >=4)
    if assessment["total_score"] >= 4:
        fb = collect_feedback(assessment)
        if fb:
            print("→ 피드백 반영하여 RAG 재검색 및 재평가")
            ctx2 = retrieve_guidelines(queries + [fb])
            assessment = evaluate_risks(profile, ctx2)
            print(f"→ 2차 평가 완료 (최고점수: {assessment['total_score']})")

    # 7) 개선 권고안
    recs = generate_recommendations(assessment)
    print("→ 개선 권고안 생성 완료")

    # 8) 리포트 생성
    build_report(desc, svc_type, assessment, recs)
    print("✅ 완료")

if __name__ == "__main__":
    main()
