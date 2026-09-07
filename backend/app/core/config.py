import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "Intelligent Invoice Analysis and Processing Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Storage paths
    IS_VERCEL: bool = bool(os.getenv("VERCEL"))
    UPLOAD_DIR: Path = Path("/tmp/uploads") if bool(os.getenv("VERCEL")) else WORKSPACE_DIR / "uploads"
    REPORT_DIR: Path = Path("/tmp/reports") if bool(os.getenv("VERCEL")) else WORKSPACE_DIR / "reports"
    DB_PATH: Path = Path("/tmp/invoices.db") if bool(os.getenv("VERCEL")) else WORKSPACE_DIR / "invoices.db"
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # 'ollama', 'openai', or 'mock'
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-production-agentic-key-95de73b5")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Confidence-Based Routing
    CONFIDENCE_AUTO_APPROVE_MIN: float = 0.90
    CONFIDENCE_REVIEW_MIN: float = 0.60
    RISK_AUTO_APPROVE_MAX: float = 30.0
    RISK_HIGH_MIN: float = 61.0
    RISK_CRITICAL_MIN: float = 81.0
    
    # Tolerances for Purchase Order matching
    PO_QUANTITY_TOLERANCE_PCT: float = 5.0  # 5% tolerance
    PO_PRICE_TOLERANCE_PCT: float = 3.0     # 3% tolerance
    
    # Tax Configuration
    DEFAULT_TAX_PERCENT: float = 18.0
    VALID_TAX_RATES: list[float] = [0.0, 5.0, 12.0, 18.0, 28.0]

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
