"""
RetinAI Backend — API Routes
Endpoints consumed by the Next.js frontend.
"""
import uuid
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.config import UPLOADS_DIR, HEATMAPS_DIR, REPORTS_DIR
from backend.app.database import (
    create_patient, list_patients, get_patient,
    create_analysis, list_analyses, get_analysis, delete_analysis_db
)
from backend.app.api.schemas import PatientCreate, PatientOut, AnalysisOut
from backend.model.predict import predict_from_pil, CLASS_NAMES
from backend.model.gradcam import generate_heatmap
from backend.app.agents.orchestrator import run_workflow

router = APIRouter()

# ── Clinical lookup tables ────────────────────────────────────────────────────
URGENCIES = [
    "Contrôle annuel",
    "Suivi 6-12 mois",
    "Sous 3 mois",
    "Sous 1 mois",
    "Urgence absolue !"
]

STAGE_DESCRIPTIONS = [
    "Aucune rétinopathie diabétique. Rétine saine, aucune lésion visible.",
    "Rétinopathie diabétique légère. Présence de microanévrismes isolés.",
    "Rétinopathie diabétique modérée. Hémorragies rétiniennes et exsudats durs détectés.",
    "Rétinopathie diabétique sévère. Hémorragies extensives et anomalies microvasculaires.",
    "Rétinopathie diabétique proliférative. Néovascularisation active, risque imminent de cécité."
]


def _generate_report(stage: int, confidence: float, patient_id: str, patient_name: str) -> str:
    """Generate a template-based clinical report (placeholder for future LLM agents)."""
    stage_text = [
        "Aucune rétinopathie diabétique",
        "Rétinopathie diabétique légère",
        "Rétinopathie diabétique modérée",
        "Rétinopathie diabétique sévère",
        "Rétinopathie diabétique proliférative"
    ]
    urgency = URGENCIES[stage]
    referable = stage >= 2

    return f"""### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : {datetime.now().strftime('%Y-%m-%d')} | **Identifiant Patient** : `{patient_id}` | **Nom** : **{patient_name}**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade {stage} / 4 - {stage_text[stage]}**
- **Indice de Confiance** : **{confidence * 100:.1f}%**
- **Niveau d'Urgence Clinique** : **{urgency}**
- **Statut d'Adressage Référable (Referable DR)** : **{"⚠️ OUI - Nécessite une consultation ophtalmologique" if referable else "✅ NON"}**

#### 2. CONSTATATIONS CLINIQUES DU FOND D'ŒIL
{STAGE_DESCRIPTIONS[stage]} L'activation Grad-CAM a localisé les régions d'intérêt correspondant au stade prédit avec un indice de confiance de {confidence * 100:.1f}%.

#### 📅 PROTOCOLE DE SUIVI & PRÉVENTION CLINIQUE (Stade {stage})
1. **Orientation** : {urgency}
2. **Examens Complémentaires** : {"OCT maculaire recommandé" if stage >= 2 else "Aucun examen complémentaire nécessaire"}
3. **Surveillance Métabolique** : Contrôle HbA1c {"rigoureux" if stage >= 2 else "de routine"}

> ⚠️ **IMPORTANT** : Ce rapport est généré automatiquement par une IA d'assistance clinique. Les résultats doivent être validés par un ophtalmologue qualifié.

*Note : Le module d'agents LangGraph (RAG PubMed, Clinical Agent, Critic Agent) sera intégré prochainement pour enrichir ce rapport avec des citations scientifiques et une analyse approfondie.*"""


# ── Health Check ──────────────────────────────────────────────────────────────

@router.get("/")
async def health_check():
    return {"status": "ok", "service": "RetinAI Backend", "model": "dr_model_v2.onnx"}


# ── Patient Endpoints ─────────────────────────────────────────────────────────

@router.get("/api/patients", response_model=list[PatientOut])
async def get_patients():
    return list_patients()


@router.post("/api/patients", response_model=PatientOut)
async def add_patient(patient: PatientCreate):
    existing = get_patient(patient.id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Le patient {patient.id} existe déjà.")
    create_patient(patient.id, patient.name, patient.birthdate, patient.gender)
    return get_patient(patient.id)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/api/dashboard", response_model=list[AnalysisOut])
async def get_dashboard():
    analyses = list_analyses()
    for a in analyses:
        pdf_filename = f"{a['id']}.pdf"
        if (REPORTS_DIR / pdf_filename).exists():
            a["pdf_url"] = f"/static/reports/{pdf_filename}"
        else:
            a["pdf_url"] = None
    return analyses


# ── Analyze ───────────────────────────────────────────────────────────────────

@router.post("/api/analyze", response_model=AnalysisOut)
async def analyze_image(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):
    # Validate patient exists
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} introuvable.")

    # Generate unique ID
    analysis_id = f"AN-{uuid.uuid4().hex[:9].upper()}"
    timestamp = datetime.now().isoformat()

    # Save uploaded image
    ext = Path(file.filename).suffix or ".jpg"
    image_filename = f"{analysis_id}{ext}"
    image_path = UPLOADS_DIR / image_filename
    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # ── Run ONNX inference ────────────────────────────────────────────────
    result = predict_from_pil(str(image_path))
    stage = result["stage"]
    confidence = result["confidence"]
    probs = result["probabilities"]

    # ── Generate Grad-CAM heatmap ─────────────────────────────────────────
    heatmap_filename = f"{analysis_id}_heatmap.jpg"
    heatmap_path = HEATMAPS_DIR / heatmap_filename
    generate_heatmap(str(image_path), str(heatmap_path), stage=stage)

    # ── Build analysis record ─────────────────────────────────────────────
    referable = 1 if stage >= 2 else 0
    urgency = URGENCIES[stage]
    description = f"Stade {stage} - {STAGE_DESCRIPTIONS[stage]}"
    
    # ── Run LangGraph multi-agent report workflow ─────────────────────────
    workflow_inputs = {
        "analysis_id": analysis_id,
        "patient_id": patient_id,
        "patient_name": patient["name"],
        "patient_gender": patient["gender"],
        "patient_birthdate": patient.get("birthdate"),
        "image_path": str(image_path),
        "heatmap_path": str(heatmap_path),
        "stage": stage,
        "confidence": confidence
    }
    
    try:
        workflow_result = run_workflow(workflow_inputs)
        clinical_report = workflow_result.get("clinical_report")
        pdf_url = workflow_result.get("pdf_url")
    except Exception as e:
        print(f"[API Workflow Error] {e} — falling back to static report template.")
        clinical_report = _generate_report(stage, confidence, patient_id, patient["name"])
        pdf_url = None

    analysis_data = {
        "id": analysis_id,
        "patient_id": patient_id,
        "stage": stage,
        "confidence": confidence,
        "referable": referable,
        "urgency": urgency,
        "image_path": f"/static/uploads/{image_filename}",
        "heatmap_path": f"/static/heatmaps/{heatmap_filename}",
        "description": description,
        "clinical_report": clinical_report,
        "pdf_url": pdf_url,
        "created_at": timestamp,
    }

    # Save to database
    create_analysis(analysis_data)

    # Return with patient info
    analysis_data["patient_name"] = patient["name"]
    analysis_data["patient_gender"] = patient["gender"]

    return analysis_data


@router.delete("/api/analyses/{analysis_id}")
async def delete_analysis_endpoint(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse introuvable.")

    # 1. Delete original fundus image from disk
    if analysis.get("image_path"):
        filename = Path(analysis["image_path"]).name
        image_filepath = UPLOADS_DIR / filename
        if image_filepath.exists() and image_filepath.is_file():
            try:
                image_filepath.unlink()
            except Exception as e:
                print(f"[Delete Error] Could not remove image file {image_filepath}: {e}")

    # 2. Delete heatmap image from disk
    if analysis.get("heatmap_path"):
        filename = Path(analysis["heatmap_path"]).name
        heatmap_filepath = HEATMAPS_DIR / filename
        if heatmap_filepath.exists() and heatmap_filepath.is_file():
            try:
                heatmap_filepath.unlink()
            except Exception as e:
                print(f"[Delete Error] Could not remove heatmap file {heatmap_filepath}: {e}")

    # 3. Delete PDF report from disk
    pdf_filename = f"{analysis_id}.pdf"
    pdf_filepath = REPORTS_DIR / pdf_filename
    if pdf_filepath.exists() and pdf_filepath.is_file():
        try:
            pdf_filepath.unlink()
        except Exception as e:
            print(f"[Delete Error] Could not remove PDF file {pdf_filepath}: {e}")

    # 4. Remove from SQLite DB
    delete_analysis_db(analysis_id)

    return {"status": "ok", "message": f"Analyse {analysis_id} supprimee avec succes."}
