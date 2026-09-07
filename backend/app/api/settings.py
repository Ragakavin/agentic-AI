from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.schemas import SystemSettingsUpdate
from backend.app.core.config import settings

router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("")
def get_system_settings():
    return {
        "confidence_auto_approve_min": settings.CONFIDENCE_AUTO_APPROVE_MIN,
        "confidence_review_min": settings.CONFIDENCE_REVIEW_MIN,
        "risk_auto_approve_max": settings.RISK_AUTO_APPROVE_MAX,
        "risk_high_min": settings.RISK_HIGH_MIN,
        "risk_critical_min": settings.RISK_CRITICAL_MIN,
        "po_quantity_tolerance_pct": settings.PO_QUANTITY_TOLERANCE_PCT,
        "po_price_tolerance_pct": settings.PO_PRICE_TOLERANCE_PCT,
        "default_tax_rate": settings.DEFAULT_TAX_PERCENT,
        "valid_tax_rates": settings.VALID_TAX_RATES,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "llm_base_url": settings.LLM_BASE_URL
    }

@router.post("")
def update_system_settings(req: SystemSettingsUpdate):
    if req.confidence_auto_approve_min is not None:
        settings.CONFIDENCE_AUTO_APPROVE_MIN = req.confidence_auto_approve_min
    if req.confidence_review_min is not None:
        settings.CONFIDENCE_REVIEW_MIN = req.confidence_review_min
    if req.risk_auto_approve_max is not None:
        settings.RISK_AUTO_APPROVE_MAX = req.risk_auto_approve_max
    if req.po_quantity_tolerance_pct is not None:
        settings.PO_QUANTITY_TOLERANCE_PCT = req.po_quantity_tolerance_pct
    if req.po_price_tolerance_pct is not None:
        settings.PO_PRICE_TOLERANCE_PCT = req.po_price_tolerance_pct
    if req.default_tax_rate is not None:
        settings.DEFAULT_TAX_PERCENT = req.default_tax_rate
    if req.llm_provider is not None:
        settings.LLM_PROVIDER = req.llm_provider
    if req.llm_model is not None:
        settings.LLM_MODEL = req.llm_model
    if req.llm_base_url is not None:
        settings.LLM_BASE_URL = req.llm_base_url

    return {
        "message": "System settings updated successfully.",
        "settings": get_system_settings()
    }
