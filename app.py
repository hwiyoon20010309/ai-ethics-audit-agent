# app.py
# LangGraph 워크플로우를 연결하고 실행하는 파일
import json
from langgraph.graph import StateGraph, END
from agents.service_analysis import service_analysis_agent
from agents.ethical_risk_diagnosis import ethical_risk_agent
from agents.improvement_suggestion import improvement_agent
from agents.report_generation import report_agent

# === State 정의 ===
class State(dict):
    pass

# === 그래프 설계 ===
graph = StateGraph(State)

graph.add_node("ServiceAnalysis", service_analysis_agent)
graph.add_node("EthicalRiskDiagnosis", ethical_risk_agent)
graph.add_node("ImprovementSuggestion", improvement_agent)
graph.add_node("ReportGeneration", report_agent)

graph.set_entry_point("ServiceAnalysis")
graph.add_edge("ServiceAnalysis", "EthicalRiskDiagnosis")
graph.add_edge("EthicalRiskDiagnosis", "ImprovementSuggestion")
graph.add_edge("ImprovementSuggestion", "ReportGeneration")
graph.add_edge("ReportGeneration", END)

app = graph.compile()

# === 실행 ===
if __name__ == "__main__":
    print("🧭 AI Ethics Audit Agent Started")
    ai_type = input("🔍 진단할 AI 서비스 유형을 선택하세요 (생성형/예측형/추천형):\n> ")
    description = input("🧠 해당 AI 서비스에 대한 간략한 설명을 입력하세요:\n> ")

    result = app.invoke({
        "service_info": {
            "type": ai_type,
            "description": description
        }
    })

    print("\n✅ 최종 리포트 생성 완료!\n")
    print(result["report_summary"])