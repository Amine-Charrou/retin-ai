<div align="center">

# 🔬 RetinAI

### AI-powered Diabetic Retinopathy Screening Platform

*Deep Learning classification · Multi-agent clinical reporting · PubMed RAG*

![Status](https://img.shields.io/badge/status-in%20development-yellow?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-multi--agent-8B5CF6?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

</div>

---

## Overview

**RetinAI** is an end-to-end clinical decision support platform for diabetic retinopathy screening. It combines a Deep Learning model for fundus image classification with a multi-agent AI pipeline that produces structured medical reports — complete with scientific citations, Grad-CAM visual explanations, and tailored follow-up recommendations.

> **Why it matters** — 537 million people live with diabetes worldwide. 1 in 3 will develop diabetic retinopathy. It is the leading cause of blindness in working-age adults, yet **95% of vision loss is preventable** with early detection. In Morocco alone, there is only 1 ophthalmologist per 25,000 inhabitants. RetinAI is designed to bring expert-level screening to any general practitioner, anywhere.

---

## How It Works

```
Fundus Image (upload)
        │
        ▼
┌───────────────────┐
│   Deep Learning   │  EfficientNet-B4 / Vision Transformer
│   Classification  │  Stages 0–4  +  Grad-CAM heatmap
└────────┬──────────┘
         │  stage · confidence · heatmap
         ▼
┌─────────────────────────────────────────────────────────┐
│                  Agentic Layer  (LangGraph)              │
│                                                         │
│   ┌──────────────┐      ┌───────────────────┐           │
│   │  RAG Agent   │      │  Clinical Agent   │  parallel │
│   │  PubMed      │      │  Interpretation   │           │
│   └──────────────┘      └───────────────────┘           │
│   ┌──────────────┐      ┌───────────────────┐           │
│   │ Grad-CAM     │      │  Report Agent     │  parallel │
│   │ Vision Agent │      │  PDF generation   │           │
│   └──────────────┘      └───────────────────┘           │
└─────────────────────────────────────────────────────────┘
         │
         ▼
  Structured Medical Report (PDF)
  diagnosis · citations · annotated heatmap · follow-up plan
```

---

## DR Severity Stages

| Stage | Name | Description | Clinical Action |
|-------|------|-------------|----------------|
| 0 | No DR | Healthy retina | Annual screening |
| 1 | Mild DR | Microaneurysms only | Follow-up in 6–12 months |
| 2 | Moderate DR | Hemorrhages, exudates | Ophthalmologist in 3–6 months |
| 3 | Severe DR | Extensive hemorrhages | **Ophthalmologist within 1 month** |
| 4 | Proliferative DR | Neovascularization | **Immediate consultation** |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Deep Learning | PyTorch · EfficientNet-B4 / ViT · Grad-CAM |
| Agentic Pipeline | LangGraph · LangChain |
| LLM — Orchestrator & Agents | Llama 3.3 70B via Groq |
| LLM — Vision (Grad-CAM description) | Gemini 2.0 Flash |
| RAG Source | PubMed E-utilities API |
| Backend API | FastAPI · Uvicorn |
| PDF Report | ReportLab |
| Frontend | Next.js · TailwindCSS |
| Database | PostgreSQL (patient records) |

---

## Project Structure

```
retin-ai/
│
├── backend/                        # FastAPI + LangGraph agentic layer
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Settings, API keys
│   │   │
│   │   ├── agents/                 # LangGraph multi-agent system
│   │   │   ├── state.py            # RetinAIState — shared graph state
│   │   │   ├── orchestrator.py     # LangGraph graph definition & runner
│   │   │   ├── rag_agent.py        # PubMed search + retrieval agent
│   │   │   ├── clinical_agent.py   # Clinical interpretation agent
│   │   │   ├── gradcam_agent.py    # Grad-CAM visual description agent
│   │   │   └── report_agent.py     # Report compilation + PDF agent
│   │   │
│   │   ├── tools/                  # Agent-callable tools
│   │   │   ├── pubmed_tool.py      # PubMed E-utilities wrapper
│   │   │   └── pdf_tool.py         # ReportLab PDF generator
│   │   │
│   │   └── api/                    # REST endpoints
│   │       ├── routes.py           # /analyze, /report, /health
│   │       └── schemas.py          # Pydantic request/response models
│   │
│   ├── model/                      # Deep Learning inference
│   │   ├── predict.py              # Inference pipeline
│   │   ├── gradcam.py              # Grad-CAM heatmap generator
│   │   └── weights/                # Model weights (not tracked in git)
│   │
│   ├── tests/                      # Unit & integration tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       # Next.js web application
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx            # Landing page
│   │   │   ├── upload/             # Image upload & analysis flow
│   │   │   └── report/             # Report viewer
│   │   │
│   │   ├── components/             # Reusable UI components
│   │   │   ├── ImageUploader.tsx
│   │   │   ├── HeatmapViewer.tsx
│   │   │   ├── StageIndicator.tsx
│   │   │   └── ReportCard.tsx
│   │   │
│   │   └── lib/                    # API client, utilities
│   │       └── api.ts              # Backend API calls
│   │
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docs/                           # Documentation & research
│   ├── architecture.md
│   └── dataset.md
│
├── docker-compose.yml              # Full stack orchestration
├── .env.example                    # Environment variables template
├── .gitignore
└── README.md
```

---

## API Keys Required (all free tiers)

| Service | Purpose | Free Tier | Link |
|---------|---------|-----------|------|
| Groq | LLM inference (Llama 3.3 70B) | 14,400 req/day | [console.groq.com](https://console.groq.com) |
| Google AI Studio | Vision LLM (Gemini 2.0 Flash) | 1,500 req/day | [aistudio.google.com](https://aistudio.google.com) |
| PubMed E-utilities | Medical literature RAG | Free + email quota | [ncbi.nlm.nih.gov](https://www.ncbi.nlm.nih.gov/home/develop/api/) |

---

## Roadmap

**Phase 1 — Agentic Backend**
- [ ] `RetinAIState` & LangGraph graph
- [ ] RAG Agent (PubMed)
- [ ] Clinical Interpretation Agent
- [ ] Grad-CAM Vision Agent
- [ ] Report & PDF Agent
- [ ] FastAPI endpoints

**Phase 2 — Deep Learning**
- [ ] Dataset preparation (Kaggle DR dataset)
- [ ] EfficientNet-B4 training
- [ ] Grad-CAM integration
- [ ] Model evaluation & benchmarking

**Phase 3 — Frontend**
- [ ] Upload & analysis flow
- [ ] Heatmap visualization
- [ ] Report viewer & PDF download

**Phase 4 — Clinical Validation**
- [ ] Ophthalmologist review
- [ ] Performance metrics (AUC, sensitivity, specificity)

---

## Academic Context

This project is developed as part of the **Artificial Intelligence Engineering** program at **ENSA Agadir**, Morocco.

---

## Authors

- **Amine Charrou** — [github.com/Amine-Charrou](https://github.com/Amine-Charrou)
- **Ahmed Chmourk**

---

## License

MIT © 2025 RetinAI
