"""
RetinAI Backend — LangGraph Shared State
Defines the schema for variables exchanged across the clinical agent nodes.
"""
from typing import TypedDict, List, Dict, Any, Optional

class RetinAIState(TypedDict):
    # ── Input Data ────────────────────────────────────────────────────────────
    analysis_id: str       # Unique analysis ID (e.g. AN-123456789)
    patient_id: str
    patient_name: str
    patient_gender: str
    patient_birthdate: Optional[str]
    
    image_path: str        # Absolute local path to original fundus image
    heatmap_path: str      # Absolute local path to Grad-CAM heatmap
    stage: int             # Predicted DR stage (0-4)
    confidence: float      # ONNX classification confidence (0.0 - 1.0)
    
    # ── Agent Outputs ─────────────────────────────────────────────────────────
    gradcam_description: str             # Visual review by Gemini 2.0 Flash
    pubmed_citations: List[Dict[str, Any]] # Reference papers fetched from PubMed
    clinical_interpretation: str         # Structured diagnostic summary by Llama 3.3
    care_plan: str                       # Patient follow-up guidelines
    
    # ── Critic & Safety Node ──────────────────────────────────────────────────
    critic_feedback: Optional[str]        # Refusal/warning comments from Critic
    is_validated: bool                   # True if report satisfies guidelines
    iterations: int                      # Track loop count to prevent infinite loops
    
    # ── Final Output Data ─────────────────────────────────────────────────────
    clinical_report: str                 # Final combined Markdown report
    pdf_path: str                        # Absolute local path to generated PDF
    pdf_url: str                         # Frontend-accessible URL path for the PDF
