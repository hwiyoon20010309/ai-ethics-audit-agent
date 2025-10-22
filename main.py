# main.py
import os
from agents.type_classifier import classify_service
from agents.service_analyzer import analyze_service
from agents.risk_factor_extractor import extract_risk_factors
from agents.rag_retriever import retrieve_guidelines
from agents.risk_evaluator import evaluate_risks
from agents.human_feedback import collect_feedback
from agents.recommendation_generator import generate_recommendations
from agents.report_builder import generate_report
from agents.service_crawler import crawl_service_info


def main():
    print("\n🧭 [AI 윤리성 리스크 진단 시스템 시작]\n")

    # Step 0️⃣ 서비스명 입력 및 자동 크롤링
    service_name = input("🔍 분석할 AI 서비스명을 입력하세요: ").strip()
    if not service_name:
        print("🚫 서비스명이 입력되지 않았습니다.")
        return

    print(f"\n🌐 '{service_name}' 관련 웹 데이터를 수집하고 있습니다...\n")
    service_description = crawl_service_info(service_name)

    if not service_description:
        print("⚠️ 서비스 정보를 가져오지 못했습니다. 수동 입력으로 진행합니다.")
        service_info = analyze_service()
    else:
        print("✅ 웹 기반 서비스 요약 완료.\n")
        # 크롤링된 텍스트를 기존 analyze_service() 형식에 맞게 매핑
        service_info = {
            "name": service_name,
            "purpose": service_description,
            "features": ["자동 문장 생성", "문체 변환", "키워드 추출"],  # 임시 기본값
            "data_input": "웹 텍스트, 제품 설명, 사용자 입력",
            "data_output": "생성된 텍스트, 문장 추천",
            "model": "GPT 기반 생성형 언어모델"
        }

    # Step 1️⃣ 서비스 유형 분류
    classification = classify_service(service_info["purpose"])
    service_info["type"] = classification.get("type", "분류 실패")

    print(f"\n✅ 서비스 유형: {service_info['type']}")
    print(f"📋 주요 기능: {', '.join(service_info['features'])}")

    # Step 2️⃣ 리스크 요인 추출
    risk_factors = extract_risk_factors(service_info)
    print(f"\n⚠️ 잠재적 리스크 요인 식별됨: {', '.join(risk_factors)}")

    # Step 3️⃣ 윤리 가이드라인 검색 (RAG)
    guideline_contexts = retrieve_guidelines(risk_factors)

    # Step 4️⃣ 리스크 평가 (스코어 산출)
    risk_assessment = evaluate_risks(service_info, guideline_contexts)

    # Step 5️⃣ 사용자 피드백 루프 (Human-in-the-loop)
    feedback = collect_feedback(risk_assessment)
    if feedback:
        print("\n🔁 피드백 기반 재평가 수행 중...")
        risk_assessment = evaluate_risks(service_info, guideline_contexts, feedback=feedback)

    # Step 6️⃣ 개선 권고안 생성
    recommendations = generate_recommendations(risk_assessment, guideline_contexts)

    # Step 7️⃣ 리포트 출력 (Markdown + PDF)
    generate_report(service_info, risk_assessment, recommendations)

    print("\n🎯 윤리성 리스크 진단 완료 — 결과 보고서가 outputs/reports 폴더에 생성되었습니다.\n")


if __name__ == "__main__":
    main()
