# agents/service_analyzer.py
def analyze_service():
    print("\n📘 [AI 서비스 개요 입력]\n서비스의 전반적인 정보를 단계별로 입력하세요.\n")

    service_info = {
        "name": input("1️⃣ 서비스명: "),
        "purpose": input("2️⃣ 서비스 목적: "),
        "users": input("3️⃣ 대상 사용자: "),
        "features": input("4️⃣ 핵심 기능 (쉼표로 구분): ").split(","),
        "input_data": input("5️⃣ 입력 데이터 유형: "),
        "output_data": input("6️⃣ 출력 데이터 유형: "),
        "data_source": input("7️⃣ 데이터 출처: "),
        "model_type": input("8️⃣ 사용 AI 모델 / 기술 스택: "),
        "use_case": input("9️⃣ 결과 활용 경로: "),
        "ethical_concerns": input("🔟 윤리적 고려사항 (있다면): "),
    }

    print("\n✅ 서비스 개요 입력 완료.")
    return service_info
