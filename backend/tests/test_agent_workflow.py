"""
RetinAI Backend — Agent Workflow Integration Test
Verifies the orchestration, agent states, and PDF compilation.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.agents.orchestrator import run_workflow
from backend.app.config import REPORTS_DIR


def test_agentic_workflow():
    print("=== STARTING AGENTIC WORKFLOW TEST ===")
    
    # 1. Mock inputs matching standard FastAPI format
    mock_input = {
        "analysis_id": "AN-TESTTEST9",
        "patient_id": "P-4421",
        "patient_name": "Amine Charrou",
        "patient_gender": "M",
        "patient_birthdate": "1998-05-12",
        "image_path": str(PROJECT_ROOT / "backend" / "model" / "test_images" / "test_grade2.jpg"),
        "heatmap_path": str(PROJECT_ROOT / "backend" / "model" / "test_images" / "test_grade2.jpg"), # Mock heatmap with original image for test
        "stage": 2,
        "confidence": 0.943
    }
    
    # Check if mock images exist
    if not os.path.exists(mock_input["image_path"]):
         print(f"Warning: Mock image path {mock_input['image_path']} not found. PDF will generate without image placeholders.")
         mock_input["image_path"] = None
         mock_input["heatmap_path"] = None

    # 2. Execute workflow
    result = run_workflow(mock_input)
    
    # 3. Assertions
    assert "clinical_report" in result, "Workflow result missing 'clinical_report'"
    assert "pdf_path" in result, "Workflow result missing 'pdf_path'"
    assert "pdf_url" in result, "Workflow result missing 'pdf_url'"
    assert "pubmed_citations" in result, "Workflow result missing 'pubmed_citations'"
    
    print("\n--- Diagnostic Assertions Checked ---")
    print(f"Validated by Critic Agent: {result.get('is_validated')}")
    print(f"Generated PDF path: {result.get('pdf_path')}")
    print(f"Generated PDF URL: {result.get('pdf_url')}")
    
    # Verify PDF file is created and has size > 0
    pdf_path = Path(result.get("pdf_path"))
    assert pdf_path.exists(), f"PDF report file does not exist on disk: {pdf_path}"
    assert pdf_path.stat().st_size > 0, f"Generated PDF report is empty: {pdf_path}"
    
    print("\n=== AGENTIC WORKFLOW TEST COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    test_agentic_workflow()
