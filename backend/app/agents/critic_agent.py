"""
RetinAI Backend — Safety Critic Agent
Audits reports for safety warnings, clinical coherence, and standard-of-care guidelines.
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.app.agents.state import RetinAIState

# ── Groq Setup ────────────────────────────────────────────────────────────────
HAS_GROQ = False
try:
    if os.getenv("GROQ_API_KEY"):
        HAS_GROQ = True
except Exception as e:
    print(f"[Safety Critic Setup Warning] {e}")


def safety_critic_agent(state: RetinAIState) -> dict:
    """
    Critic Agent Node.
    Validates clinical report components, ensuring proper urgency guidelines and legal disclaimers.
    """
    stage = state.get("stage", 0)
    clinical_interpretation = state.get("clinical_interpretation", "")
    care_plan = state.get("care_plan", "")
    iterations = state.get("iterations", 0)
    
    # ── Rule-based Safety Audit (Programmatic constraints) ────────────────────
    feedback_notes = []
    
    # Rule 1: Stage 4 must contain urgent care timeline
    if stage == 4:
        stage4_keywords = ["urgence", "immédiat", "heures", "24", "48"]
        if not any(k in care_plan.lower() for k in stage4_keywords):
            feedback_notes.append("Le plan de soins pour un Stade 4 doit impérativement spécifier une consultation d'urgence sous 24 à 48 heures.")
            
    # Rule 2: Referable DR (Stage >= 2) must refer to an ophthalmologist
    if stage >= 2:
        referable_keywords = ["ophtalmologue", "spécialiste", "consultation"]
        if not any(k in care_plan.lower() for k in referable_keywords):
            feedback_notes.append("Les stades référables (Stade >= 2) doivent spécifier un adressage vers un ophtalmologue.")
            
    # ── LLM-based Safety Audit (If Groq is available and iterations < 2) ──────
    if HAS_GROQ and iterations < 2:
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", (
                    "Vous êtes un médecin inspecteur et auditeur de sécurité clinique (Critic Agent) pour RetinAI.\n"
                    "Votre rôle est d'analyser le diagnostic et le plan de soins proposés par le système et de valider "
                    "leur cohérence réglementaire et médicale (directives de l'OMS et de l'American Academy of Ophthalmology).\n\n"
                    "Instructions :\n"
                    "1. Répondez exclusivement au format JSON suivant :\n"
                    "   {{\n"
                    "     \"is_validated\": true / false,\n"
                    "     \"feedback\": \"Vos remarques de correction si non validé, ou vide si validé.\"\n"
                    "   }}\n"
                    "2. Critères de Non-Validation :\n"
                    "   - Contradiction flagrante entre le stade (ex: Stade 4) et l'urgence (ex: Contrôle annuel).\n"
                    "   - Absence de recommandation d'OCT pour les stades modérés ou sévères.\n"
                    "   - Termes non professionnels ou manque de clarté clinique.\n"
                    "3. N'incluez aucune phrase d'accompagnement en dehors du bloc JSON."
                )),
                ("user", (
                    "Rapport en cours d'audit :\n"
                    "- Stade : {stage} / 4\n"
                    "- Interprétation clinique : {clinical_interpretation}\n"
                    "- Plan de soins : {care_plan}\n\n"
                    "Audit (JSON) :"
                ))
            ])
            
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.0, # Purely deterministic for audit
                max_tokens=200
            )
            
            # Request JSON output from Groq
            chain = prompt_template | llm.bind(response_format={"type": "json_object"})
            
            import json
            response = chain.invoke({
                "stage": stage,
                "clinical_interpretation": clinical_interpretation,
                "care_plan": care_plan
            })
            
            audit_result = json.loads(response.content.strip())
            
            # Combine programmatic and LLM feedback
            is_validated = audit_result.get("is_validated", True)
            llm_feedback = audit_result.get("feedback", "")
            
            if feedback_notes:
                is_validated = False
                combined_feedback = "; ".join(feedback_notes)
                if llm_feedback:
                    combined_feedback += " | LLM Notes: " + llm_feedback
            else:
                combined_feedback = llm_feedback if not is_validated else None
                
            return {
                "is_validated": is_validated,
                "critic_feedback": combined_feedback,
                "iterations": iterations + 1
            }
            
        except Exception as e:
            print(f"[Safety Critic Error] {e} — Proceeding with rule-based safety evaluation.")
            
    # ── Rule-based Validation Fallback ────────────────────────────────────────
    is_validated = len(feedback_notes) == 0
    combined_feedback = "; ".join(feedback_notes) if not is_validated else None
    
    return {
        "is_validated": is_validated,
        "critic_feedback": combined_feedback,
        "iterations": iterations + 1
    }
