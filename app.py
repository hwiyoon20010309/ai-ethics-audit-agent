"""
AI Ethics Audit Agent - Main Execution Script
Author: 최휘윤
Description: 멀티에이전트 기반 AI 윤리 리스크 진단 및 개선 리포트 생성 시스템
"""

import os
from dotenv import load_dotenv
from agents.service_analysis import analyze_service
from agents.ethical_risk_diagnosis import diagnose_ethics
from agents.improvement_suggestion import suggest_improvements
from agents.report_generation import generate_report

# .env 파일 로드 (OpenAI API Key 등)
load_dotenv()

def main():
    print("\n🧭 [AI 윤리성 리스크 진단 시스템 시작]\n")

    # 1️⃣ 사용자 입력 (서비스 유형)
    service_type = input("진단할 AI 서비스 유형을 입력하세요 (예: 생성형 AI, 추천형 AI, 예측형 AI): ")

    # 초기 상태 정의
    state = {
        "service_info": None,
        "risk_assessment": None,
        "recommendations": None,
        "report_summary": None,
        "report_final": None
    }

    # 2️⃣ 서비스 분석
    print("\n[1] 서비스 분석 중...")
    state["service_info"] = analyze_service(service_type)

    # 3️⃣ 윤리 리스크 진단
    print("[2] 윤리 리스크 평가 중...")
    state["risk_assessment"] = diagnose_ethics(state["service_info"])

    # 4️⃣ 개선 권고안 생성
    print("[3] 개선 권고안 생성 중...")
    state["recommendations"] = suggest_improvements(state["risk_assessment"])

    # 5️⃣ 보고서 생성
    print("[4] 보고서 생성 중...")
    state["report_final"] = generate_report(state)

    # 출력 경로
    output_path = os.path.join("outputs", f"{service_type}_ethics_report.md")
    os.makedirs("outputs", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(state["report_final"])

    print(f"\n✅ 윤리 리스크 진단이 완료되었습니다.")
    print(f"📄 결과 보고서: {output_path}\n")

if __name__ == "__main__":
    main()
