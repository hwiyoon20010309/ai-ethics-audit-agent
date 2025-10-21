# 🧭 AI 윤리성 리스크 진단 (AI Ethics Audit Agent)

본 프로젝트는 AI 윤리성 리스크 진단 에이전트(AI Ethics Audit Agent)를 설계하고 구현한 실습 프로젝트입니다.  
LangGraph 기반 멀티 에이전트 시스템을 통해 특정 AI 서비스 유형(생성형 AI, 추천형 AI, 예측형 AI)을 진단하고,  
국제 AI 윤리 가이드라인(EU AI Act, OECD, UNESCO)에 따라 윤리 리스크 분석 및 개선 권고안을 자동 생성합니다.

---

## 📘 Overview

- **Objective:**  
  특정 AI 서비스 유형을 대상으로 윤리 리스크(편향성, 프라이버시 침해, 투명성 부족 등)를 분석하고  
  EU AI Act, OECD, UNESCO 기준을 적용하여 개선 권고안 및 리포트를 자동 생성하는 시스템 개발

- **Methods:**  
  Prompt Engineering, Multi-Agent Workflow (LangGraph), Rule-based Ethical Scoring  

- **Tools:**  
  LangGraph, LangChain, OpenAI GPT-4o-mini, Pandas, ReportLab

---

## ⚙️ Features

- 🤖 **서비스 분석 자동화** — AI 서비스의 목적, 입력 데이터, 주요 기능을 분석  
- ⚖️ **윤리 리스크 진단** — 편향성, 프라이버시, 투명성 등 10대 윤리 항목별 평가  
- 💡 **개선 권고안 제안** — 국제 AI 윤리 가이드라인(EU, OECD, UNESCO) 기반 개선 방향 제시  
- 📊 **자동 리포트 생성** — 평가 결과를 Markdown 및 PDF 형태로 리포트화  

---

## 🧩 Tech Stack 

| Category   | Details |
|-------------|----------|
| **Framework** | LangGraph, LangChain, Python 3.11 |
| **LLM** | GPT-4o-mini via OpenAI API |
| **Retrieval** | FAISS, Chroma |
| **Embedding** | OpenAIEmbedding (text-embedding-3-small) |
| **Visualization** | Mermaid, Graphviz |
| **Report** | ReportLab, pypandoc |

---

## 🧠 Agents
 
- **Service Analysis Agent** : AI 서비스 개요 및 기능 분석  
- **Ethical Risk Diagnosis Agent** : 윤리 기준(EU AI Act, OECD, UNESCO)에 따른 리스크 평가  
- **Improvement Suggestion Agent** : 항목별 개선 방향 제시  
- **Report Generation Agent** : 평가 결과 및 개선안 기반 리포트 작성 (Markdown/PDF)

---

## 🧮 State 

- `service_info` : 사용자가 입력한 AI 서비스 설명 및 기능 요약  
- `risk_assessment` : 윤리 항목별 리스크 평가 결과 (점수/코멘트)  
- `recommendations` : 개선 권고안 리스트  
- `report_summary` : 요약 리포트 (결과 요약 문단)  
- `report_final` : 최종 리포트(Markdown 또는 PDF 파일)

---

## 🧭 Architecture
```mermaid
graph TD
A[사용자 입력: AI 서비스 설명] --> B[Service Analysis Agent]
B --> C[Ethical Risk Diagnosis Agent]
C --> D[Improvement Suggestion Agent]
D --> E[Report Generation Agent]
E --> F[Output: Ethics Risk Report (PDF/MD)]
```

## Directory Structure
ai-ethics-audit-agent/
├── agents/
│   ├── service_analysis.py
│   ├── ethical_risk_diagnosis.py
│   ├── improvement_suggestion.py
│   └── report_generation.py
├── prompts/
│   ├── service_analysis_prompt.txt
│   ├── ethical_risk_prompt.txt
│   ├── improvement_prompt.txt
│   └── report_prompt.txt
├── data/                  # AI 윤리 가이드라인 문서 (EU, OECD, UNESCO)
├── outputs/               # 리포트 결과 저장 (Markdown/PDF)
├── app.py                 # 실행 스크립트
├── requirements.txt
└── README.md
