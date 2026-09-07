from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db, Base, engine
from backend.app.database.seed import seed_database
from backend.app.models.models import Invoice
from backend.app.agents.intake_agent import intake_agent
from backend.app.agents.orchestrator import orchestrator
from backend.app.core.config import settings

router = APIRouter(prefix="/demo", tags=["Demo Simulation"])

BENCHMARK_CASES = {
    "clean": {
        "title": "Clean Invoice (ABC Technologies - ₹59,000)",
        "file": "invoice_1_clean.pdf",
        "description": "Standard compliance, exact PO match, 18% GST -> Auto-Approve"
    },
    "po_mismatch": {
        "title": "PO Mismatch (XYZ Solutions - ₹125,000)",
        "file": "invoice_2_po_mismatch.pdf",
        "description": "Quantity 120 vs PO 100 (+20% diff, tolerance 5%) -> Review Required"
    },
    "duplicate": {
        "title": "Duplicate Invoice (ABC Technology - INV-10025)",
        "file": "invoice_3_duplicate.pdf",
        "description": "Fuzzy & exact similarity 94% to existing record -> Critical Risk"
    },
    "tax_mismatch": {
        "title": "Tax Mismatch (Delta Systems - ₹102,400)",
        "file": "invoice_4_tax_mismatch.pdf",
        "description": "28% GST billed vs expected 18% statutory schedule -> Review Required"
    }
}

@router.get("/cases")
def list_demo_cases():
    return [
        {"key": k, **v} for k, v in BENCHMARK_CASES.items()
    ]

@router.post("/trigger/{case_key}")
async def trigger_demo_case(case_key: str, db: Session = Depends(get_db)):
    """Run an automated demo test case through the complete 10-agent pipeline."""
    if case_key not in BENCHMARK_CASES:
        raise HTTPException(status_code=400, detail=f"Unknown demo case. Choose from: {list(BENCHMARK_CASES.keys())}")

    case = BENCHMARK_CASES[case_key]
    file_path = settings.UPLOAD_DIR / case["file"]
    
    # Ensure sample file exists
    if not file_path.exists():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"%PDF-1.4\n% Demo File for: {case['title']}\n")

    # Run intake agent
    intake_res = intake_agent.run(db, file_path, case["file"])
    internal_id = intake_res["internal_db_id"]

    # Run full multi-agent orchestrator
    process_res = await orchestrator.process_invoice(db, internal_id)

    return {
        "case_key": case_key,
        "title": case["title"],
        "intake": intake_res,
        "analysis": process_res
    }

@router.post("/reset")
def reset_demo_database(db: Session = Depends(get_db)):
    """Reset database tables and re-seed the benchmark initial state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database(db)
    return {"message": "Demo database successfully reset and seeded with benchmark records."}
