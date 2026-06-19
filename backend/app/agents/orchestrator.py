"""
RetinAI Backend — LangGraph Agentic Orchestrator
Defines the StateGraph and transitions for the multi-agent clinical workspace.
"""
from langgraph.graph import StateGraph, END

from backend.app.agents.state import RetinAIState
from backend.app.agents.gradcam_agent import gradcam_vision_agent
from backend.app.agents.rag_agent import pubmed_rag_agent
from backend.app.agents.clinical_agent import clinical_interpretation_agent
from backend.app.agents.followup_agent import followup_agent
from backend.app.agents.critic_agent import safety_critic_agent
from backend.app.agents.report_agent import report_compiler_agent


def route_after_critic(state: RetinAIState):
    """
    Decides whether to compiler the final report or loop back for clinical correction.
    """
    is_validated = state.get("is_validated", True)
    iterations = state.get("iterations", 0)
    
    if is_validated:
        print("[Orchestrator] Report safety checks passed. Forwarding to compiler.")
        return "compiler"
    elif iterations >= 2:
        print(f"[Orchestrator] Safety warning raised: '{state.get('critic_feedback')}'. Max iterations reached. Forcing compilation with warnings.")
        return "compiler"
    else:
        print(f"[Orchestrator] Safety warning raised: '{state.get('critic_feedback')}'. Loop back to refine clinical interpretation.")
        return "clinical_interpretation"


# ── Define Graph ──────────────────────────────────────────────────────────────
builder = StateGraph(RetinAIState)

# 1. Register all nodes
builder.add_node("gradcam_vision", gradcam_vision_agent)
builder.add_node("pubmed_rag", pubmed_rag_agent)
builder.add_node("clinical_interpretation", clinical_interpretation_agent)
builder.add_node("followup", followup_agent)
builder.add_node("critic", safety_critic_agent)
builder.add_node("compiler", report_compiler_agent)

# 2. Build the edges
# To be robust across multiple LangGraph versions, we configure a linear flow 
# leading to the critic node, which then executes the conditional feedback loop.
builder.set_entry_point("gradcam_vision")

builder.add_edge("gradcam_vision", "pubmed_rag")
builder.add_edge("pubmed_rag", "clinical_interpretation")
builder.add_edge("clinical_interpretation", "followup")
builder.add_edge("followup", "critic")

# Add conditional feedback edge from safety critic
builder.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "compiler": "compiler",
        "clinical_interpretation": "clinical_interpretation"
    }
)

builder.add_edge("compiler", END)

# Compile graph
workflow = builder.compile()


def run_workflow(inputs: dict) -> dict:
    """
    Executes the multi-agent clinical report compilation synchronously.
    
    Inputs dict should contain:
        analysis_id: str
        patient_id: str
        patient_name: str
        patient_gender: str
        patient_birthdate: Optional[str]
        image_path: str
        heatmap_path: str
        stage: int
        confidence: float
    """
    # Initialize orchestration counter variables
    inputs["iterations"] = 0
    inputs["is_validated"] = False
    inputs["critic_feedback"] = None
    
    print(f"\n[Orchestrator] Initializing RetinAI Agentic Workflow for Analysis {inputs.get('analysis_id')}...")
    final_state = workflow.invoke(inputs)
    print("[Orchestrator] Workflow completed successfully.\n")
    return final_state


if __name__ == "__main__":
    # Test execution locally
    mock_input = {
        "analysis_id": "AN-TESTORCH1",
        "patient_id": "P-4421",
        "patient_name": "Amine Charrou",
        "patient_gender": "M",
        "patient_birthdate": "1998-05-12",
        "image_path": None,
        "heatmap_path": None,
        "stage": 3,
        "confidence": 0.962
    }
    result = run_workflow(mock_input)
    print("\n--- Final Compiled Report ---")
    print(result.get("clinical_report"))
    print("\n--- Output PDF file URL ---")
    print(result.get("pdf_url"))
