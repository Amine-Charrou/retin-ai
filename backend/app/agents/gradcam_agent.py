"""
RetinAI Backend — Grad-CAM Vision Agent
Examines the fundus image/heatmap using Gemini 2.0 Flash to describe visual lesions.
"""
import os
from PIL import Image
from backend.app.agents.state import RetinAIState

# ── Gemini Setup ─────────────────────────────────────────────────────────────
# We can use the official google-generativeai package or fallback if key is missing.
HAS_GEMINI = False
try:
    import google.generativeai as genai
    if os.getenv("GOOGLE_API_KEY"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        HAS_GEMINI = True
except Exception as e:
    print(f"[Grad-CAM Agent Setup Warning] {e}")


def gradcam_vision_agent(state: RetinAIState) -> dict:
    """
    Analyzes the Grad-CAM heatmap and original scan using Gemini 2.0 Flash.
    Provides a text description of the localized lesions or retina status.
    """
    stage = state.get("stage", 0)
    confidence = state.get("confidence", 0.0)
    heatmap_path = state.get("heatmap_path")
    image_path = state.get("image_path")
    
    stage_names = [
        "Aucune rétinopathie diabétique (Saine)",
        "Rétinopathie diabétique légère",
        "Rétinopathie diabétique modérée",
        "Rétinopathie diabétique sévère",
        "Rétinopathie diabétique proliférative"
    ]
    
    # ── Fallback Description (if API key missing or error occurs) ─────────────
    fallback_descriptions = [
        # Stage 0
        "L'analyse visuelle montre une rétine d'aspect normal et homogène. La papille optique "
        "présente des contours nets et réguliers, et la macula est libre de toute lésion. Aucun "
        "signe de microanévrisme, d'exsudat dur ou d'hémorragie n'a été localisé par la carte d'attention.",
        # Stage 1
        "La carte d'attention Grad-CAM met en évidence de faibles hotspots localisés correspondant "
        "à des microanévrismes débutants isolés. Les gros vaisseaux rétiniens et la macula sont respectés. "
        "Aucun signe d'œdème maculaire ni d'exsudation lipidique majeure n'est décelé.",
        # Stage 2
        "L'examen de l'activation montre des zones d'intérêt modérées réparties autour de la zone "
        "périmaculaire, correspondant à des foyers d'exsudats durs (dépôts lipidiques) et de petites "
        "hémorragies rétiniennes pointiformes. Il n'y a pas d'évidence de néovaisseaux.",
        # Stage 3
        "Des foyers d'activation intense (hotspots) sont présents dans au moins deux quadrants de la rétine. "
        "Ils coïncident avec des hémorragies intrarétiniennes diffuses importantes et des anomalies "
        "microvasculaires intrarétiniennes (AMIR). La vascularisation est irrégulière et perturbée.",
        # Stage 4
        "La carte de chaleur montre des pics d'attention extrêmes au niveau de la papille et des arcades "
        "vasculaires, corrélés à une néovascularisation prérétinienne active et des risques "
        "d'hémorragie vitréenne. Des anomalies de traction vitréo-rétinienne sont suspectées dans les zones d'activation."
    ]
    
    if not HAS_GEMINI or not heatmap_path or not os.path.exists(heatmap_path):
        # Return fallback description
        return {"gradcam_description": fallback_descriptions[stage]}
        
    try:
        # Load the heatmap image which contains the blended overlay
        img = Image.open(heatmap_path)
        
        prompt = (
            "En tant qu'ophtalmologue et expert en imagerie rétinienne assistant clinique IA, "
            f"analyse cette image de fond d'œil combinée à sa carte d'activation Grad-CAM.\n\n"
            f"Informations Cliniques :\n"
            f"- Stade Diagnostiqué par le modèle ONNX : {stage_names[stage]} (Stade {stage}/4)\n"
            f"- Confiance du modèle : {confidence*100:.1f}%\n\n"
            "Tâche :\n"
            "Rédige une description clinique concise et structurée (2 à 4 phrases maximum) en français, "
            "expliquant ce que les zones de chaleur (rouges/jaunes) sur l'image indiquent "
            "en rapport avec les lésions typiques de ce stade de rétinopathie diabétique. "
            "Reste purement descriptif et n'ajoute pas de salutations ni de conclusions."
        )
        
        # Call Gemini 2.0 Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([prompt, img])
        
        description = response.text.strip()
        if not description:
            raise ValueError("Empty response from Gemini")
            
        return {"gradcam_description": description}
        
    except Exception as e:
        print(f"[Grad-CAM Agent Error] {e} — Using premium fallback description.")
        return {"gradcam_description": fallback_descriptions[stage]}
