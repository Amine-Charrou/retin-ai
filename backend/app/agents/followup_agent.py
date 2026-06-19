"""
RetinAI Backend — Follow-up & Care Plan Agent
Generates clinical guidelines, monitoring intervals, and safety instructions based on DR stage.
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
    print(f"[Follow-up Agent Setup Warning] {e}")


def followup_agent(state: RetinAIState) -> dict:
    """
    Follow-up Agent node.
    Generates action-oriented follow-up instructions, specialist timelines, and metabolic checks.
    """
    stage = state.get("stage", 0)
    
    # ── Fallback care plan (if API key missing or error occurs) ───────────────
    fallback_care_plans = [
        # Stage 0
        "1. **Rythme de Surveillance** : Contrôle systématique du fond d'œil par examen annuel.\n"
        "2. **Équilibre Métabolique** : Maintien d'un contrôle glycémique stable (cible HbA1c < 7%) et autosurveillance tensionnelle régulière.\n"
        "3. **Prévention Clinique** : Sensibilisation du patient aux facteurs de risque cardiovasculaires et maintien d'une activité physique régulière.",
        
        # Stage 1
        "1. **Rythme de Surveillance** : Nouveau contrôle du fond d'œil recommandé dans 6 à 12 mois selon l'évolution clinique.\n"
        "2. **Équilibre Métabolique** : Renforcement du contrôle de la glycémie (cible HbA1c < 7.0%) et de la pression artérielle (cible < 130/80 mmHg).\n"
        "3. **Prévention Clinique** : Consultation de sensibilisation et d'éducation thérapeutique auprès du médecin traitant ou d'un diabétologue.",
        
        # Stage 2
        "1. **Orientation Spécialisée** : Consultation recommandée chez un ophtalmologue dans un délai de 3 à 6 mois.\n"
        "2. **Examens Complémentaires** : Réalisation conseillée d'une Tomographie par Cohérence Optique (OCT) maculaire pour écarter tout œdème sous-clinique.\n"
        "3. **Surveillance Strict** : Optimisation thérapeutique avec contrôle trimestriel de l'HbA1c et bilan lipidique annuel complet.",
        
        # Stage 3
        "1. **Orientation Spécialisée** : Consultation impérative chez un ophtalmologue dans un délai maximum de 1 mois.\n"
        "2. **Examens Complémentaires** : Angiographie à la fluorescéine et Tomographie par Cohérence Optique (OCT) maculaire bilatérale.\n"
        "3. **Mesures Métaboliques** : Bilan biologique rénal (microalbuminurie des 24h), réévaluation rapide du traitement du diabète avec un spécialiste.",
        
        # Stage 4
        "1. **Orientation Spécialisée** : Adressage en urgence pour consultation spécialisée ophtalmologique sous 24 à 48 heures.\n"
        "2. **Intervention Thérapeutique** : Évaluation immédiate pour traitement par panphotocoagulation laser (PPR) ou injections intravitréennes d'anti-VEGF.\n"
        "3. **Consignes de Sécurité** : Repos physique, évitement des efforts violents et de la prise d'antiagrégants (sauf indication cardiologique majeure), surveillance de toute baisse brutale d'acuité visuelle."
    ]
    
    fallback_text = fallback_care_plans[stage]
    
    if not HAS_GROQ:
        return {"care_plan": fallback_text}
        
    try:
        # Prompt definition
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "Vous êtes un diabétologue et médecin coordinateur expert de la plateforme RetinAI.\n"
                "Votre rôle est d'élaborer le protocole de suivi et de prévention clinique adapté au stade de "
                "rétinopathie diabétique diagnostiqué, rédigé en français.\n\n"
                "Règles d'écriture :\n"
                "1. Structurez vos recommandations sous forme de liste numérotée à 3 points :\n"
                "   1. Orientation Spécialisée / Rythme de Surveillance (indiquez des délais cliniques précis).\n"
                "   2. Examens Complémentaires Recommandés (OCT, angiographie, etc.).\n"
                "   3. Mesures Métaboliques & Consignes (HbA1c, tension, néphropathie, etc.).\n"
                "2. Soyez direct, clair et axé sur l'action.\n"
                "3. N'ajoutez aucune introduction ni conclusion, commencez directement par le point 1."
            )),
            ("user", (
                "Données Diagnostiques :\n"
                "- Stade de Rétinopathie Diabétique : Stade {stage} / 4\n"
                "- Description Clinique des lésions : {clinical_interpretation}\n\n"
                "Protocole de Suivi (en français) :"
            ))
        ])
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=400
        )
        
        chain = prompt_template | llm
        
        response = chain.invoke({
            "stage": stage,
            "clinical_interpretation": state.get("clinical_interpretation", "")
        })
        
        care_plan = response.content.strip()
        if not care_plan:
            raise ValueError("Empty response from ChatGroq")
            
        return {"care_plan": care_plan}
        
    except Exception as e:
        print(f"[Follow-up Agent Error] {e} — Using premium care plan fallback.")
        return {"care_plan": fallback_text}
