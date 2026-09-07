from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.session import get_db
from backend.app.models.models import AgentRun, AgentToolCall
from backend.app.schemas.schemas import AgentRunOut

router = APIRouter(prefix="/agents", tags=["Agents Monitor"])

AGENTS_LIST = [
    {"name": "Invoice Intake Agent", "role": "Document ingestion, format detection, size & hash verification"},
    {"name": "Document Extraction Agent", "role": "OCR layout parsing, field structuring, confidence scoring"},
    {"name": "Invoice Validation Agent", "role": "Mandatory fields check & deterministic math verification"},
    {"name": "Tax Validation Agent", "role": "GST/CGST/SGST/VAT rate & calculation compliance verification"},
    {"name": "Duplicate Detection Agent", "role": "Fuzzy string matching & binary hash duplicate detection"},
    {"name": "Purchase Order Matching Agent", "role": "3-way line item match against PO database with tolerances"},
    {"name": "Vendor Verification Agent", "role": "Vendor master check, tax ID validation & historical spend deviation"},
    {"name": "Fraud and Anomaly Detection Agent", "role": "12 fraud & anomaly indicators evaluation & Risk Score (0-100)"},
    {"name": "AI Reasoning Agent", "role": "Multi-agent evidence synthesis & explainable decision logic via LLM"},
    {"name": "Decision Agent", "role": "Confidence-based routing (APPROVE/REVIEW/REJECT) & review task dispatch"}
]

@router.get("/overview")
def get_agents_overview(db: Session = Depends(get_db)):
    """Return live status, execution stats, and tool count for each specialized agent."""
    overview = []
    for ag in AGENTS_LIST:
        runs = db.query(AgentRun).filter(AgentRun.agent_name == ag["name"]).all()
        total_runs = len(runs)
        avg_time = int(sum(r.execution_time_ms for r in runs) / total_runs) if total_runs else 0
        failed = sum(1 for r in runs if r.status == "FAILED")
        warnings = sum(1 for r in runs if r.status == "WARNING")
        completed = sum(1 for r in runs if r.status == "COMPLETED")
        
        # Tool calls executed by this agent
        tool_count = db.query(AgentToolCall).join(AgentRun).filter(AgentRun.agent_name == ag["name"]).count()

        overview.append({
            "name": ag["name"],
            "role": ag["role"],
            "status": "IDLE" if total_runs == 0 else ("WARNING" if warnings > 0 else "ACTIVE"),
            "total_runs": total_runs,
            "avg_latency_ms": avg_time,
            "completed_count": completed,
            "warning_count": warnings,
            "failed_count": failed,
            "total_tool_calls": tool_count
        })
    return overview

@router.get("/runs", response_model=list[AgentRunOut])
def get_recent_agent_runs(limit: int = 50, db: Session = Depends(get_db)):
    runs = db.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(limit).all()
    return runs
