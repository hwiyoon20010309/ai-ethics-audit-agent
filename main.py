import os
from typing import Any, Dict

from agents.type_classifier import classify_service
from agents.service_analyzer import analyze_service
from agents.risk_factor_extractor import extract_risk_factors
from agents.rag_retriever import retrieve_guidelines
from agents.risk_evaluator import evaluate_risks
from agents.human_feedback import collect_feedback
from agents.recommendation_generator import generate_recommendations
from agents.report_builder import generate_report
from agents.service_crawler import crawl_service_info

DEFAULT_FEATURES = ["자동 문장 생성", "문체 변환", "키워드 추출"]

# -------------------------------------------------------------------
# 🔧 유틸리티 함수들
# -------------------------------------------------------------------

def normalize_service_info(si: Any, service_name: str) -> Dict[str, Any]:
    """service_info를 항상 dict로 표준화"""
    if si is None:
        return {
            "name": service_name,
            "purpose": "",
            "features": DEFAULT_FEATURES,
            "data_input": "웹 텍스트, 사용자 입력",
            "data_output": "생성된 문장, 요약 텍스트",
            "model": "GPT 기반 생성형 언어모델",
            "type": "",
        }

    if isinstance(si, dict):
        return {
            "name": si.get("name", service_name),
            "purpose": si.get("purpose", ""),
            "features": si.get("features", DEFAULT_FEATURES),
            "data_input": si.get("data_input", "웹 텍스트, 사용자 입력"),
            "data_output": si.get("data_output", "생성된 문장, 요약 텍스트"),
            "model": si.get("model", "GPT 기반 생성형 언어모델"),
            "type": si.get("type", si.get("service_type", "")),
        }

    return {
        "name": service_name,
        "purpose": str(si),
        "features": DEFAULT_FEATURES,
        "data_input": "웹 텍스트, 사용자 입력",
        "data_output": "생성된 문장, 요약 텍스트",
        "model": "GPT 기반 생성형 언어모델",
        "type": "",
    }


def _coerce_score(x):
    """점수를 float으로 안전 변환"""
    try:
        return float(x)
    except Exception:
        return None


def print_risk_summary_table(title: str, assessment: dict):
    """평가 결과를 콘솔에 표 형태로 출력"""
    if not isinstance(assessment, dict) or not assessment:
        print(f"\n[{title}] 평가 결과가 비어있습니다.\n")
        return

    print(f"\n[{title}] 윤리 리스크 요약")
    print("-" * 70)
    print(f"{'항목':<28} {'점수':<6} {'설명'}")
    print("-" * 70)

    rows = []
    for k, v in assessment.items():
        if isinstance(v, dict):
            s = _coerce_score(v.get("score", None))
            c = v.get("comment", "")
        else:
            s = _coerce_score(v)
            c = ""
        rows.append((k, s, c))

    rows.sort(key=lambda x: (x[1] is None, -(x[1] or 0)))
    for name, score, comment in rows:
        score_txt = "-" if score is None else (f"{score:.1f}" if isinstance(score, float) else str(score))
        print(f"{name:<28} {score_txt:<6} {comment}")

    print("-" * 70)


# -------------------------------------------------------------------
# 🧭 메인 로직
# -------------------------------------------------------------------

def main():
    print("\n🧭 [AI 윤리성 리스크 진단 시스템 시작]\n")

    # === 0️⃣ state 초기화 ===
    state: Dict[str, Any] = {
        "service_name": None,
        "service_info": None,
        "risk_factors": None,
        "policy_context": None,
        "risk_assessment": None,
        "human_feedback": None,
        "recommendations": None,
    }

    # === 1️⃣ 서비스명 입력 ===
    state["service_name"] = input("🔍 분석할 AI 서비스명을 입력하세요: ").strip()
    if not state["service_name"]:
        print("🚫 서비스명이 입력되지 않았습니다.")
        return

    print(f"\n🌐 '{state['service_name']}' 관련 웹 데이터를 수집하고 있습니다...\n")
    description = crawl_service_info(state["service_name"])

    # === 2️⃣ 서비스 정보 세팅 ===
    if not description:
        print("⚠️ 서비스 정보를 가져오지 못했습니다. 수동 입력으로 진행합니다.")
        analyzed = analyze_service()
        state["service_info"] = normalize_service_info(analyzed, state["service_name"])
    else:
        print("✅ 웹 기반 서비스 요약 완료.\n")
        raw_info = {
            "name": state["service_name"],
            "purpose": description,
            "features": DEFAULT_FEATURES,
            "data_input": "웹 텍스트, 사용자 입력",
            "data_output": "생성된 문장, 요약 텍스트",
            "model": "GPT 기반 생성형 언어모델",
        }
        state["service_info"] = normalize_service_info(raw_info, state["service_name"])

    # === 3️⃣ 서비스 유형 분류 ===
    try:
        classification = classify_service(state["service_info"].get("purpose", ""))
        state["service_info"]["type"] = classification.get("type", "분류 실패")
    except AttributeError:
        print("⚠️ service_info 구조 오류 발생 → 자동 복구 시도 중...")
        state["service_info"] = normalize_service_info(state["service_info"], state["service_name"])
        classification = classify_service(state["service_info"].get("purpose", ""))
        state["service_info"]["type"] = classification.get("type", "분류 실패")

    print(f"\n✅ 서비스 유형: {state['service_info']['type']}")
    print(f"📋 주요 기능: {', '.join(state['service_info']['features'])}")

    # === 4️⃣ 리스크 요인 추출 ===
    state["risk_factors"] = extract_risk_factors(state["service_info"])
    print(f"\n⚠️ 잠재적 리스크 요인 식별됨: {', '.join(state['risk_factors'])}")

    # === 5️⃣ 윤리 가이드라인 RAG 검색 ===
    try:
        state = retrieve_guidelines(state)
    except AttributeError:
        print("⚠️ RAG 검색 중 state 구조 오류 → 복구 후 재시도")
        if not isinstance(state, dict):
            state = {"policy_context": ""}
        state = retrieve_guidelines(state)

    # === 6️⃣ 리스크 평가 ===
    try:
        state = evaluate_risks(state)
    except AttributeError:
        print("⚠️ 평가 중 state 구조 오류 → 복구 후 재시도")
        state["risk_assessment"] = {}
        state = evaluate_risks(state)

    # ✅ 콘솔에 전체 점수 출력
    print_risk_summary_table("초기 평가", state.get("risk_assessment", {}))

    # === 7️⃣ 고위험 항목 표시 ===
    ra = state.get("risk_assessment", {}) or {}

    def _score_of(v):
        if isinstance(v, dict):
            return _coerce_score(v.get("score", None))
        return _coerce_score(v)

    high_risk = {}
    for k, v in ra.items():
        s = _score_of(v)
        if s is not None and s >= 4:
            if not isinstance(v, dict):
                v = {"score": s, "comment": ""}
            high_risk[k] = v

    if high_risk:
        print("\n⚠️ 일부 항목의 윤리 리스크 점수가 높게 평가되었습니다.")
        for k, v in high_risk.items():
            print(f"   - {k}: {v['score']}점 ({v['comment']})")

        # === 8️⃣ 사용자 피드백 수집 ===
        state["human_feedback"] = collect_feedback(state["risk_assessment"])

        if state["human_feedback"]:
            print(f"\n🧩 피드백 수집 완료 → '{state['human_feedback']}'")
            print("\n🔁 피드백 기반 재검색 및 재평가 수행 중...")
            try:
                state = retrieve_guidelines(state)
                final_state = evaluate_risks(state)
                final_assessment = final_state.get("risk_assessment", {})
                print_risk_summary_table("재평가(피드백 반영)", final_assessment)
            except Exception as e:
                print(f"⚠️ 피드백 반영 중 오류 발생: {e}")
                final_assessment = ra
    else:
        print("\n✅ 모든 윤리 항목이 허용 범위 내에 있습니다. 피드백 루프를 생략합니다.")
        state["human_feedback"] = None
        final_assessment = ra

    # === 9️⃣ 개선 권고안 생성 (최종 평가 기준) ===
    state["recommendations"] = generate_recommendations(
        final_assessment,
        state.get("policy_context")
    )

    # === 🔟 보고서 생성 ===
    if not isinstance(state.get("service_info"), dict):
        print("⚠️ service_info가 문자열로 변환되어 복구 중...")
        state["service_info"] = normalize_service_info(state["service_info"], state["service_name"])

    try:
        generate_report(
            state["service_info"],
            ra,                     # 초기 평가
            final_assessment,        # 최종 평가
            state.get("recommendations", "개선 권고안 없음"),
            state.get("human_feedback")
        )
        print("\n🎯 윤리성 리스크 진단 완료 — 결과 보고서가 outputs/reports 폴더에 생성되었습니다.\n")

    except Exception as e:
        print(f"🚨 보고서 생성 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
