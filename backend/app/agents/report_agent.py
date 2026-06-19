"""
RetinAI Backend — Report Compiler Agent
Formats the markdown clinical report and compiles the final PDF document.
"""
from datetime import datetime
from pathlib import Path
from backend.app.agents.state import RetinAIState
from backend.app.config import REPORTS_DIR
from backend.app.tools.pdf_tool import generate_pdf_report


def report_compiler_agent(state: RetinAIState) -> dict:
    """
    Compiler Agent node.
    Synthesizes text findings from clinical and follow-up agents into a structured Markdown document.
    Triggers the ReportLab PDF generator tool and returns references to the file.
    """
    analysis_id = state.get("analysis_id", "AN-UNKNOWN")
    patient_id = state.get("patient_id", "P-UNKNOWN")
    patient_name = state.get("patient_name", "Patient")
    patient_gender = state.get("patient_gender", "M")
    patient_birthdate = state.get("patient_birthdate")
    
    stage = state.get("stage", 0)
    confidence = state.get("confidence", 0.0)
    clinical_interpretation = state.get("clinical_interpretation", "")
    care_plan = state.get("care_plan", "")
    citations = state.get("pubmed_citations", [])
    
    original_img = state.get("image_path")
    heatmap_img = state.get("heatmap_path")
    
    stage_text = [
        "Aucune rétinopathie diabétique",
        "Rétinopathie diabétique légère",
        "Rétinopathie diabétique modérée",
        "Rétinopathie diabétique sévère",
        "Rétinopathie diabétique proliférative"
    ]
    
    urgency_levels = [
        "Contrôle annuel",
        "Suivi 6-12 mois",
        "Sous 3 mois",
        "Sous 1 mois",
        "Urgence absolue !"
    ]
    
    urgency = urgency_levels[stage]
    referable = "⚠️ OUI - Nécessite une consultation ophtalmologique" if stage >= 2 else "✅ NON"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # ── 1. Compile PubMed citations in Markdown ────────────────────────────────
    pubmed_md = ""
    if citations:
        for i, c in enumerate(citations):
            pubmed_md += (
                f"- **Source** : {c['authors']} ({c['year']}). *{c['title']}* — "
                f"publié dans **{c['journal']}**.\n"
                f"  *Conclusion de l'étude* : Retrouvez l'article sur [PubMed]({c['url']}) (PMID: {c['pmid']}).\n"
            )
    else:
        pubmed_md = "Aucune citation PubMed disponible."
        
    # ── 2. Format the Markdown Clinical Report ────────────────────────────────
    report_markdown = f"""### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : {date_str} | **Identifiant Patient** : `{patient_id}` | **Nom** : **{patient_name}**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade {stage} / 4 - {stage_text[stage]}**
- **Indice de Confiance** : **{confidence * 100:.1f}%**
- **Niveau d'Urgence Clinique** : **{urgency}**
- **Statut d'Adressage Référable (Referable DR)** : **{referable}**

#### 2. CONSTATATIONS CLINIQUES DU FOND D'ŒIL
{clinical_interpretation}

#### 3. CORRÉLATIONS SCIENTIFIQUES (PubMed)
{pubmed_md}

#### 📅 PROTOCOLE DE SUIVI & PRÉVENTION CLINIQUE (Stade {stage} - {stage_text[stage].split(' ')[-1]})
{care_plan}

> ⚠️ **IMPORTANT** : Ce rapport est généré automatiquement par une intelligence artificielle d'assistance au diagnostic clinique. Les résultats et la carte d'activation Grad-CAM doivent impérativement être vérifiés et validés par un ophtalmologue qualifié."""

    # ── 3. Compile PDF using pdf_tool ─────────────────────────────────────────
    pdf_filename = f"{analysis_id}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename
    
    # Prep state dictionaries for the pdf_tool input
    patient_dict = {
        "id": patient_id,
        "name": patient_name,
        "gender": patient_gender,
        "birthdate": patient_birthdate or "N/A"
    }
    
    analysis_dict = {
        "id": analysis_id,
        "stage": stage,
        "confidence": confidence,
        "urgency": urgency,
        "clinical_report": report_markdown,
        "created_at": datetime.now().isoformat()
    }
    
    # Generate the actual PDF on disk
    generate_pdf_report(
        output_path=str(pdf_path),
        patient=patient_dict,
        analysis=analysis_dict,
        original_img_path=original_img,
        heatmap_img_path=heatmap_img
    )
    
    return {
        "clinical_report": report_markdown,
        "pdf_path": str(pdf_path),
        "pdf_url": f"/static/reports/{pdf_filename}"
    }
