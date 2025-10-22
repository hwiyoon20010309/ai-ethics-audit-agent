# 🧭 AI 윤리성 리스크 진단 (AI Ethics Audit Agent)

본 프로젝트는 **AI 윤리성 리스크 진단 에이전트(AI Ethics Audit Agent)** 를 설계하고 구현한 실습 프로젝트입니다.  
LangGraph 기반 멀티 에이전트 시스템을 통해 **AI 서비스 유형(생성형, 추천형, 예측형)** 을 자동 분류하고,  
국제 AI 윤리 가이드라인(EU AI Act, OECD, UNESCO)에 따라 **윤리 리스크 분석·피드백·개선 권고안 생성**을 자동화합니다.  

본 프로젝트는 **RAG (Retrieval-Augmented Generation)** 기반으로 문서 근거를 검색하고,  
**Human Feedback Loop**을 통해 재평가와 개선안을 반복적으로 보완하는 **AI 윤리 진단 워크플로우**를 구현합니다.

---

## 📘 Overview

- **Objective**  
  AI 서비스를 대상으로 편향성, 공정성, 프라이버시, 투명성 등의 윤리 리스크를 진단하고  
  국제 기준(EU, OECD, UNESCO)에 따른 **정량 평가 + 개선안 자동화 리포트**를 생성합니다.

- **Methods**  
  - Multi-Agent Workflow (LangGraph 기반)
  - RAG (Retrieval-Augmented Generation)
  - Human Feedback 기반 재평가 (Human-in-the-loop)
  - Prompt Engineering & Context Reasoning

- **Tools & Frameworks**  
  LangGraph · LangChain · GPT-4o-mini · ChromaDB · ReportLab · Python 3.11

---

## ⚙️ Features

| 기능 | 설명 |
|------|------|
| 🤖 **서비스 자동 분석** | 입력된 설명으로부터 AI 서비스 유형 자동 분류 및 구조 분석 |
| ⚖️ **윤리 리스크 진단** | 10대 항목별 리스크 점수(1~5) 및 코멘트 생성 |
| 📚 **RAG 기반 가이드라인 검색** | EU, OECD, UNESCO 윤리 문서를 근거로 평가 수행 |
| 🗣️ **Human Feedback 재평가 루프** | 사용자의 콘솔 피드백을 반영한 재검색 및 재평가 |
| 💡 **개선 권고안 생성** | 가이드라인 조항 기반 구체적 개선 방향 제시 |
| 📊 **리포트 자동화** | Markdown / PDF 형태의 윤리 진단 보고서 자동 출력 |

---

## 🧩 Tech Stack 

| Category | Details |
|-----------|----------|
| **Framework** | LangGraph, LangChain |
| **LLM** | GPT-4o-mini (OpenAI) |
| **Vector DB** | Chroma (FAISS backend) |
| **Embedding** | text-embedding-3-small |
| **Visualization** | Mermaid, Graphviz |
| **Report Engine** | ReportLab, Pandas |
| **Environment** | Python 3.11, dotenv(OpenAI API Key) |

---

## 🧠 Agents
 
| 단계 | Agent | 주요 역할 | 입력 | 출력 |
|------|--------|------------|-------------|-------------|
| ① | **TypeClassifierAgent** | AI 서비스 유형 자동 분류 | 서비스 설명 | `service_info["type"]` |
| ② | **ServiceAnalyzerAgent** | 목적, 입력·출력, 구조 분석 | `service_info` | `service_profile` |
| ③ | **RiskFactorExtractor** | 잠재적 윤리 리스크 요인 추출 | `service_profile` | `risk_factors` |
| ④ | **RAGRetrieverAgent** | 국제 가이드라인 근거 검색 | `risk_factors` | `policy_context` |
| ⑤ | **RiskEvaluator** | RAG 문맥 기반 윤리 점수 및 코멘트 생성 | `policy_context` | `risk_assessment` |
| ⑥ | **HumanFeedbackAgent** | 콘솔 입력 기반 사용자 피드백 수집 | `risk_assessment` | `human_feedback` |
| ⑦ | **RAGRetrieverAgent (재검색)** | 피드백 반영 재검색 | `human_feedback` | `policy_context (update)` |
| ⑧ | **RiskEvaluator (재평가)** | 피드백 반영 재평가 수행 | `policy_context + feedback` | `risk_assessment (update)` |
| ⑨ | **RecommendationGenerator** | 개선안 생성 (가이드라인 기반) | `risk_assessment` | `recommendations` |
| ⑩ | **ReportBuilder** | PDF/Markdown 보고서 생성 | `recommendations` | `report_final` |

---

## 🧮 State Definition

| State Key | Type | 생성 Agent | 사용 Agent | 설명 |
|------------|------|-------------|-------------|------|
| `service_info` | dict | User Input | TypeClassifierAgent | 사용자가 입력한 AI 서비스 기본 정보 |
| `service_profile` | dict | ServiceAnalyzerAgent | RiskFactorExtractor | 분석된 서비스 구조 및 데이터 특성 |
| `risk_factors` | dict | RiskFactorExtractor | RAGRetrieverAgent | 추출된 윤리 리스크 요인 |
| `policy_context` | str | RAGRetrieverAgent | RiskEvaluator | RAG 기반으로 검색된 정책 근거 문단 |
| `risk_assessment` | dict | RiskEvaluator | HumanFeedbackAgent / RecommendationGenerator | 항목별 점수 및 코멘트 |
| `human_feedback` | str | HumanFeedbackAgent | RAGRetrieverAgent / RiskEvaluator | 사용자 입력 피드백 |
| `recommendations` | dict | RecommendationGenerator | ReportBuilder | 개선 권고안 및 관련 조항 |
| `report_final` | file | ReportBuilder | Output | 최종 결과 리포트 (Markdown/PDF) |

---

## 🔁 Feedback-based Workflow

| 단계 | 역할 | 처리 방식 |
| --- | --- | --- |
| 1️⃣ Chunking & Embedding | 윤리 문서를 의미 단위로 벡터화 | `rag_utils.py` |
| 2️⃣ Query Generation | 윤리 항목별 질의 생성 | `RiskFactorExtractor` |
| 3️⃣ Retrieval | 관련 문단 검색 (Chroma 기반) | `RAGRetrieverAgent` |
| 4️⃣ LLM Evaluation | 문단 기반 윤리 리스크 점수화 | `RiskEvaluator` |
| 5️⃣ Human Feedback | 콘솔 입력 기반 피드백 수집 | `HumanFeedbackAgent` |
| 6️⃣ Feedback-aware Re-evaluation | 피드백을 반영해 재검색 및 재평가 수행 | `RAGRetrieverAgent + RiskEvaluator` |
| 7️⃣ Aggregation | 최종 점수 및 개선안 종합 | `RecommendationGenerator` |
| 8️⃣ Report Generation | PDF/MD 보고서 자동 생성 | `ReportBuilder` |

---

## 📊 Architecture

```mermaid
graph TD
    A["사용자 입력 (AI 서비스 설명)"] --> B["유형 분류 에이전트"]
    B --> C["서비스 분석 에이전트"]
    C --> D["리스크 요인 추출"]
    D --> E["가이드라인 검색 (RAG Retriever)"]
    E --> F["리스크 평가"]

    F -->|High Risk ≥ 4| G["Human Feedback Agent (콘솔 입력)"]
    G --> H["RAG 재검색 및 재평가 루프"]
    H --> F["RiskEvaluator (재평가)"]

    F -->|Low Risk < 4| I["개선안 제안"]
    I --> J["리포트 생성 (PDF / MD)"]
    J --> K["출력 완료"]
